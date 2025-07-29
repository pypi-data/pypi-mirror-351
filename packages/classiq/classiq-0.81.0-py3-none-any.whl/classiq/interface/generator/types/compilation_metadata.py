from pydantic import BaseModel, Field, NonNegativeInt


class CompilationMetadata(BaseModel):
    should_synthesize_separately: bool = Field(default=False)
    occurrences_number: NonNegativeInt = Field(default=1)
    unchecked: list[str] = Field(default_factory=list)
    atomic_qualifiers: list[str] = Field(
        default_factory=list, exclude=True
    )  # TODO remove after deprecation https://classiq.atlassian.net/browse/CLS-2671
