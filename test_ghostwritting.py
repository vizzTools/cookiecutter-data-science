from typing import Sequence
from hypothesis.extra import ghostwriter

## put your functions here:

def timsort(seq: Sequence[int]) -> Sequence[int]:
    """
    Example function for the hypothesis ghostwritting"""
    return sorted(seq)

ghostwriter.idempotent(timsort)
