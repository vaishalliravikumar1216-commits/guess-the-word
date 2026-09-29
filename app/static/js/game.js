// Convenience only: the spec wants upper case A-Z, so we convert as the
// player types. The server still validates every guess independently.
const guessInput = document.getElementById('guess-input');
if (guessInput) {
    guessInput.addEventListener('input', () => {
        guessInput.value = guessInput.value.toUpperCase().replace(/[^A-Z]/g, '');
    });
}