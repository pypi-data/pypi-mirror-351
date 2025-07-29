import ast
import functools
import itertools
from collections.abc import Collection, Iterator, Sequence
from contextlib import contextmanager

from classiq.interface.exceptions import (
    ClassiqExpansionError,
    ClassiqInternalExpansionError,
)
from classiq.interface.generator.functions.type_qualifier import TypeQualifier
from classiq.interface.model.allocate import Allocate
from classiq.interface.model.bind_operation import BindOperation
from classiq.interface.model.control import Control
from classiq.interface.model.invert import Invert
from classiq.interface.model.model_visitor import ModelVisitor
from classiq.interface.model.phase_operation import PhaseOperation
from classiq.interface.model.port_declaration import PortDeclaration
from classiq.interface.model.power import Power
from classiq.interface.model.quantum_expressions.amplitude_loading_operation import (
    AmplitudeLoadingOperation,
)
from classiq.interface.model.quantum_expressions.arithmetic_operation import (
    ArithmeticOperation,
)
from classiq.interface.model.quantum_expressions.quantum_expression import (
    QuantumExpressionOperation,
)
from classiq.interface.model.quantum_function_call import QuantumFunctionCall
from classiq.interface.model.quantum_statement import QuantumStatement
from classiq.interface.model.within_apply_operation import WithinApply

from classiq.model_expansions.visitors.variable_references import VarRefCollector


def _inconsistent_type_qualifier_error(
    port_name: str, expected: TypeQualifier, actual: TypeQualifier
) -> str:
    return (
        f"The type modifier of variable '{port_name}' does not conform to the function signature: "
        f"expected '{expected.name}', but found '{actual.name}'.\n"
        f"Tip: If the final role of the variable in the function matches '{expected.name}', "
        f"you may use the `unchecked` flag to instruct the compiler to disregard individual operations."
    )


class TypeQualifierValidation(ModelVisitor):
    """
    This class assumes that function calls are topologically sorted, so it traverses
    the list of function calls and infers the type qualifiers for each function call
    without going recursively into the function calls.
    The function definition ports are modified inplace.
    """

    def __init__(self, support_unused_ports: bool = True) -> None:
        self._signature_ports: dict[str, PortDeclaration] = dict()
        self._inferred_ports: dict[str, PortDeclaration] = dict()
        self._unchecked: set[str] = set()
        self._conjugation_context: bool = False
        self._support_unused_ports = (
            support_unused_ports  # could be turned off for debugging
        )

    @contextmanager
    def validate_ports(
        self, ports: Collection[PortDeclaration], unchecked: Collection[str]
    ) -> Iterator[bool]:
        for port in ports:
            if port.type_qualifier is TypeQualifier.Inferred:
                self._inferred_ports[port.name] = port
            else:
                self._signature_ports[port.name] = port
        self._unchecked.update(unchecked)

        yield len(self._inferred_ports) > 0 or any(
            port.type_qualifier is not TypeQualifier.Quantum
            for port in self._signature_ports.values()
        )

        self._set_unused_as_const()
        self._signature_ports.clear()
        self._inferred_ports.clear()
        self._unchecked.clear()

    @contextmanager
    def conjugation_context(self) -> Iterator[None]:
        previous_context = self._conjugation_context
        self._conjugation_context = True
        try:
            yield
        finally:
            self._conjugation_context = previous_context

    def _set_unused_as_const(self) -> None:
        unresolved_ports = [
            port
            for port in self._inferred_ports.values()
            if port.type_qualifier is TypeQualifier.Inferred
        ]
        if not self._support_unused_ports and len(unresolved_ports) > 0:
            raise ClassiqInternalExpansionError(
                f"Unresolved inferred ports detected: {', '.join(port.name for port in unresolved_ports)}. "
                "All ports must have their type qualifiers resolved."
            )
        for port in unresolved_ports:
            port.type_qualifier = TypeQualifier.Const

    def _validate_qualifier(self, candidate: str, qualifier: TypeQualifier) -> None:
        if self._conjugation_context and qualifier is TypeQualifier.QFree:
            qualifier = TypeQualifier.Const

        if candidate in self._inferred_ports:
            self._inferred_ports[candidate].type_qualifier = TypeQualifier.and_(
                self._inferred_ports[candidate].type_qualifier, qualifier
            )
            return

        if candidate not in self._signature_ports or candidate in self._unchecked:
            return

        signature_qualifier = self._signature_ports[candidate].type_qualifier
        if signature_qualifier is not TypeQualifier.and_(
            signature_qualifier, qualifier
        ):
            raise ClassiqExpansionError(
                _inconsistent_type_qualifier_error(
                    candidate, signature_qualifier, qualifier
                )
            )

    def run(
        self,
        ports: Collection[PortDeclaration],
        body: Sequence[QuantumStatement],
        unchecked: Collection[str],
    ) -> None:
        with self.validate_ports(ports, unchecked) as should_validate:
            if should_validate:
                self.visit(body)

    def visit_QuantumFunctionCall(self, call: QuantumFunctionCall) -> None:
        for handle, port in call.handles_with_params:
            self._validate_qualifier(handle.name, port.type_qualifier)

    def visit_Allocate(self, alloc: Allocate) -> None:
        self._validate_qualifier(alloc.target.name, TypeQualifier.QFree)

    def visit_BindOperation(self, bind_op: BindOperation) -> None:
        reduced_qualifier = self._get_reduced_qualifier(bind_op)
        for handle in itertools.chain(bind_op.in_handles, bind_op.out_handles):
            self._validate_qualifier(handle.name, reduced_qualifier)

    def _get_reduced_qualifier(self, bind_op: BindOperation) -> TypeQualifier:
        handles = itertools.chain(bind_op.in_handles, bind_op.out_handles)
        op_vars = {handle.name for handle in handles}

        signature_ports = {
            name: self._signature_ports[name]
            for name in op_vars.intersection(self._signature_ports)
        }
        known_inferred_ports = {
            name: self._inferred_ports[name]
            for name in op_vars.intersection(self._inferred_ports)
            if self._inferred_ports[name].type_qualifier is not TypeQualifier.Inferred
        }
        min_qualifier = self._get_min_qualifier(known_inferred_ports, signature_ports)
        if not all(
            port.type_qualifier is min_qualifier for port in signature_ports.values()
        ):
            raise ClassiqInternalExpansionError(
                f"Bind operation {bind_op} has inconsistent type qualifiers: "
                f"{signature_ports}, {known_inferred_ports}"
            )

        return min_qualifier

    @staticmethod
    def _get_min_qualifier(
        known_inferred_ports: dict[str, PortDeclaration],
        signature_ports: dict[str, PortDeclaration],
    ) -> TypeQualifier:
        known_ports = tuple(
            itertools.chain(signature_ports.values(), known_inferred_ports.values())
        )
        if len(known_ports) == 0:
            return TypeQualifier.Const
        elif len(known_ports) == 1:
            return known_ports[0].type_qualifier
        else:
            return functools.reduce(
                TypeQualifier.and_, (port.type_qualifier for port in known_ports)
            )

    @staticmethod
    def _extract_expr_vars(expr_op: QuantumExpressionOperation) -> list[str]:
        vrc = VarRefCollector(
            ignore_duplicated_handles=True, ignore_sympy_symbols=True, unevaluated=True
        )
        vrc.visit(ast.parse(expr_op.expression.expr))
        return [handle.name for handle in vrc.var_handles]

    def visit_ArithmeticOperation(self, arith: ArithmeticOperation) -> None:
        result_var = arith.result_var.name
        self._validate_qualifier(result_var, TypeQualifier.QFree)
        for expr_var in self._extract_expr_vars(arith):
            self._validate_qualifier(expr_var, TypeQualifier.Const)

    def visit_AmplitudeLoadingOperation(
        self, amp_load: AmplitudeLoadingOperation
    ) -> None:
        result_var = amp_load.result_var.name
        self._validate_qualifier(result_var, TypeQualifier.Quantum)
        for expr_var in self._extract_expr_vars(amp_load):
            self._validate_qualifier(expr_var, TypeQualifier.Const)

    def visit_PhaseOperation(self, phase_op: PhaseOperation) -> None:
        for expr_var in self._extract_expr_vars(phase_op):
            self._validate_qualifier(expr_var, TypeQualifier.Const)

    def visit_Control(self, control: Control) -> None:
        for control_var in self._extract_expr_vars(control):
            self._validate_qualifier(control_var, TypeQualifier.Const)
        self.visit(control.body)
        if control.else_block is not None:
            self.visit(control.else_block)

    def visit_Invert(self, invert: Invert) -> None:
        self.visit(invert.body)

    def visit_Power(self, power: Power) -> None:
        self.visit(power.body)

    def visit_WithinApply(self, within_apply: WithinApply) -> None:
        with self.conjugation_context():
            self.visit(within_apply.compute)
        self.visit(within_apply.action)
