GREEN = 'GREEN'
ORANGE = 'ORANGE'
GREY = 'GREY'
WORD_LENGTH = 5
MAX_GUESSES = 5
MAX_GAMES_PER_DAY = 3


def is_valid_guess(guess):
    """A guess must be exactly 5 letters, A-Z, upper case only."""
    return (
        len(guess) == WORD_LENGTH
        and guess.isascii()
        and guess.isalpha()
        and guess.isupper()
    )


def score_guess(target, guess):
    """
    Compare a guess to the target word.
    Returns a list of 5 colours, one per letter of the guess.
    """
    result = [GREY] * WORD_LENGTH
    remaining = []  # target letters not yet "used up" by a green match

    # Pass 1: find exact matches (green). Every target letter that
    # is NOT matched exactly goes into the 'remaining' pool.
    for i in range(WORD_LENGTH):
        if guess[i] == target[i]:
            result[i] = GREEN
        else:
            remaining.append(target[i])

    # Pass 2: for the non-green letters, mark orange only if the letter
    # is still available in the pool. Using it removes it from the pool,
    # so a letter can't be highlighted more times than it appears.
    for i in range(WORD_LENGTH):
        if result[i] == GREEN:
            continue
        if guess[i] in remaining:
            result[i] = ORANGE
            remaining.remove(guess[i])

    return result