import pytest

import vnerrant

annotator = vnerrant.load("en")


@pytest.mark.parametrize(
    "original, corrected",
    [
        ("They 're much taller than last year .", "They are much taller than last year ."), # Contraction
        ("They are much taller than last year .", "They 're much taller than last year ."), # Contraction

        ("There 're too many people in the room .", "There 's too many people in the room ."), # SVA
        ("There 're too many people in the room .", "There is too many people in the room ."), # SVA
        ("There are too many people in the room .", "There 's too many people in the room ."), # SVA

        ("There 's too many people in the room .", "There were too many people in the room ."), # Tense
        ("There 's too many people in the room .", "There was too many people in the room ."), # Tense

        ("There had too many people in the room .", "There 's too many people in the room ."), # Choice


    ],
)
def test_contraction(original, corrected):
    edits = annotator.annotate_raw(original, corrected)
    for edit in edits:
        print(edit)