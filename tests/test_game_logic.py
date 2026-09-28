import pytest
from app.game_logic import score_guess, is_valid_guess, GREEN, ORANGE, GREY


def test_all_correct():
    assert score_guess('CRANE', 'CRANE') == [GREEN] * 5


def test_no_matching_letters():
    assert score_guess('CRANE', 'MOUSY') == [GREY] * 5


def test_all_letters_present_but_wrong_positions():
    assert score_guess('STONE', 'ONEST') == [ORANGE] * 5


def test_repeated_guess_letter_only_marks_what_exists():
    # APPLE has two P's. Guessing PPPPP: only the two P's in the right
    # spots are green, the other three must be grey (not orange).
    assert score_guess('APPLE', 'PPPPP') == [GREY, GREEN, GREEN, GREY, GREY]


def test_green_uses_up_the_letter_before_orange():
    # CRANE has one E, and it's at the end. In EERIE the last E is green,
    # so the other two E's have nothing left to match and must be grey.
    assert score_guess('CRANE', 'EERIE') == [GREY, GREY, ORANGE, GREY, GREEN]


def test_repeated_target_letter_both_green():
    assert score_guess('EAGLE', 'EERIE') == [GREEN, GREY, GREY, GREY, GREEN]


def test_repeated_target_letter_both_orange():
    # SPEED has two E's, so both E's in ERASE are legitimately orange.
    assert score_guess('SPEED', 'ERASE') == [ORANGE, GREY, GREY, ORANGE, ORANGE]


def test_valid_guess_accepted():
    assert is_valid_guess('CRANE') is True


@pytest.mark.parametrize('bad_guess', ['crane', 'CRAN', 'CRANES', 'CR4NE', ''])
def test_invalid_guess_rejected(bad_guess):
    assert is_valid_guess(bad_guess) is False