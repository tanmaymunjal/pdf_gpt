import pytest
from backend.summarise_gpt import GPTSummarisation

import pytest


@pytest.mark.parametrize(
    "text, i, j, expected_subset",
    [
        ("This is a sample text to be summarized.", 5, 15, "is a sampl"),
        ("Another example", 0, 7, "Another"),
        ("", 0, 5, ""),
        ("Short", 0, 10, "Short"),  # End index is greater than text length
        ("Text", 10, 20, ""),  # Start index is greater than text length
    ],
)
def test_get_subset(text, i, j, expected_subset):
    subset = GPTSummarisation.get_subset(text, i, j)
    assert subset == expected_subset
