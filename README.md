# Guess the Word

A Wordle-style word-guessing game with separate Admin and Player roles, built with Python and Flask.

## Features

- Player registration and login, with validation on username (5+ letters, upper and lower case) and password (5+ characters, containing a letter, a digit, and one of `$ % *`).
- 20 five-letter English words seeded in the database. Each game picks one at random.
- Players get a maximum of 3 words to guess per day.
- Each guess allows 5 letters, upper case only, with a maximum of 5 guesses per word.
- Letter feedback: green (correct letter, correct position), orange (correct letter, wrong position), grey (letter not in the word).
- Win and lose messages, with the game ending when the player selects OK.
- Every guess is saved to the database with its date and result.
- Admin reports: a daily report (number of users who played, number of correct guesses) and a per-user report (date, words tried, correct guesses).

## Tech stack

- **Backend:** Python 3, Flask
- **Database:** SQLite, via Flask-SQLAlchemy
- **Auth:** Flask-Login, with Werkzeug password hashing
- **Frontend:** Jinja2 templates, vanilla CSS and JavaScript
- **Testing:** pytest (53 automated tests covering validation, game rules, and reports)

## Project structure

## Setup

```bash
git clone https://github.com/vaishalliravikumar1216-commits/guess-the-word.git
cd guess-the-word
python -m venv venv
venv\Scripts\Activate.ps1        # Windows PowerShell
pip install -r requirements.txt
mkdir instance
python seed.py
python run.py
```

Open `http://127.0.0.1:5000` in a browser.

## Default admin account

The seed script creates one admin account for testing:

- Username: `AdminUser`
- Password: `Admin1$`

New registrations through the site are always created as players. This is a deliberate choice: no player-facing route can create an admin account.

## Running the tests

```bash
python -m pytest -v
```

## Design notes

- **Daily limit timing:** a game counts against the 3-per-day limit as soon as it starts, not only when it's finished, so a player can't bypass the limit by abandoning unfavorable games.
- **Unfinished games resume:** if a player leaves mid-game, returning to the site takes them back to that same game rather than starting a new one.
- **Server-side validation:** guess and registration input is validated on the server regardless of what the browser's form restrictions allow, since client-side checks can be bypassed.