"""
Tests pin behaviour against lines whose scansion is not in dispute.

Meter detection is fuzzy by nature, so these assert the identification and the
notable substitutions rather than an exact stress string — the string changes
whenever the demotion rules are tuned, and that shouldn't fail the suite.
"""

import pytest

from scansion import (
    analyze_line, analyze_poem, analyze_word, demote_function_words,
    estimate_syllables, identify_meter, rhyme_key, rhyme_scheme, slant_score,
)


# ---------------------------------------------------------------------------
# word level
# ---------------------------------------------------------------------------

def test_dictionary_word():
    w = analyze_word("poetry")
    assert w.syllables == 3
    assert w.certain


def test_ambiguous_pronunciation_kept():
    # 'fire' is 1 or 2 syllables; poets exploit the ambiguity
    w = analyze_word("fire")
    assert w.alternatives, "second pronunciation should be preserved"


def test_oov_falls_back_and_is_flagged():
    w = analyze_word("zyzzyva")
    assert not w.certain
    assert w.syllables >= 1


@pytest.mark.parametrize("word,expected", [
    ("stone", 1),     # silent terminal e
    ("walked", 1),    # silent -ed
    ("wanted", 2),    # syllabic -ed after t
    ("table", 2),     # -le is its own syllable
    ("beautiful", 3),
])
def test_syllable_estimation(word, expected):
    assert estimate_syllables(word) == expected


def test_secondary_stress_collapses():
    # verse has two levels, not three
    w = analyze_word("information")
    assert set(w.stress) <= {"0", "1"}


# ---------------------------------------------------------------------------
# demotion
# ---------------------------------------------------------------------------

def test_function_words_demoted():
    words = demote_function_words([analyze_word(w) for w in ["the", "cat"]])
    assert words[0].stress == "0"
    assert words[0].demoted


def test_demotion_reverted_to_avoid_three_light_syllables():
    # English resists 000, so at least one demotion must be undone
    words = demote_function_words([analyze_word(w) for w in ["in", "the", "of", "sun"]])
    assert "000" not in "".join(w.stress for w in words)


def test_content_words_never_demoted():
    words = demote_function_words([analyze_word(w) for w in ["bright", "sun"]])
    assert all(not w.demoted for w in words)


# ---------------------------------------------------------------------------
# meter
# ---------------------------------------------------------------------------

def test_iambic_pentameter():
    a = analyze_line("Shall I compare thee to a summer day")
    assert a.meter.name == "iambic"
    assert a.meter.feet == 5


def test_trochaic_octameter():
    a = analyze_line("Once upon a midnight dreary, while I pondered weak and weary")
    assert a.meter.name == "trochaic"
    assert a.meter.feet == 8


def test_iambic_tetrameter():
    a = analyze_line("Whose woods these are I think I know")
    assert a.meter.name == "iambic"
    assert a.meter.feet == 4


def test_perfect_iamb_scores_high():
    m = identify_meter("0101010101")
    assert m.name == "iambic" and m.feet == 5
    assert m.confidence == 1.0


def test_empty_line_has_no_meter():
    assert identify_meter("") is None


# ---------------------------------------------------------------------------
# substitutions
# ---------------------------------------------------------------------------

def test_donne_opening_inversion():
    # the most famous inverted first foot in English
    a = analyze_line("Batter my heart, three-personed God, for you")
    kinds = [s.kind for s in a.substitutions]
    assert any("opening jolt" in k for k in kinds)


def test_spondee_detected():
    a = analyze_line("Batter my heart, three-personed God, for you")
    assert any("spondee" in s.kind for s in a.substitutions)


def test_regular_line_has_few_substitutions():
    a = analyze_line("The curfew tolls the knell of parting day")
    assert len(a.substitutions) <= 2


# ---------------------------------------------------------------------------
# caesura
# ---------------------------------------------------------------------------

def test_caesura_found_at_punctuation():
    a = analyze_line("To err is human, to forgive divine")
    assert a.caesura is not None


def test_no_caesura_without_punctuation():
    a = analyze_line("Whose woods these are I think I know")
    assert a.caesura is None


# ---------------------------------------------------------------------------
# rhyme
# ---------------------------------------------------------------------------

def test_full_rhyme_shares_key():
    assert rhyme_key("know") == rhyme_key("though")


def test_non_rhyme_differs():
    assert rhyme_key("orange") != rhyme_key("door")


def test_slant_rhyme_scores_partial():
    s = slant_score("room", "storm")
    assert 0 < s < 1


def test_frost_stanza_scheme():
    lines = [
        "Whose woods these are I think I know",
        "His house is in the village though",
        "He will not see me stopping here",
        "To watch his woods fill up with snow",
    ]
    assert "".join(rhyme_scheme(lines)).upper() == "AABA"


# ---------------------------------------------------------------------------
# whole poem
# ---------------------------------------------------------------------------

def test_poem_reports_dominant_meter():
    poem = "\n".join([
        "Whose woods these are I think I know",
        "His house is in the village though",
        "He will not see me stopping here",
        "To watch his woods fill up with snow",
    ])
    r = analyze_poem(poem)
    assert "iambic" in r["dominant_meter"]
    assert r["line_count"] == 4


def test_blank_lines_ignored():
    r = analyze_poem("First line here\n\n\nSecond line here")
    assert r["line_count"] == 2


def test_marked_rows_align():
    a = analyze_line("Whose woods these are")
    top, bottom = a.marked.split("\n")
    assert abs(len(top) - len(bottom)) <= 2
