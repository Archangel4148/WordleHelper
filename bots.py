from collections import Counter

from wordle_tools import WordleState, load_word_lists, WordleGame

VERBOSE = False

class WordleBot:
    def __init__(self):
        pass

    def guess(self, wordle_state: WordleState, guessable_words: list[str]) -> str:
        raise NotImplementedError("Subclasses must implement the guess method.")


class SimonBot(WordleBot):
    POSITIONAL_BONUSES = [
        {'A': 2, 'S': 1, 'T': 1},  # Position 0 (1st letter)
        {'R': 2, 'O': 1, 'T': 1},  # Position 1 (2nd letter)
        {'I': 2, 'E': 1, 'N': 1},  # Position 2 (3rd letter)
        {'E': 2, 'A': 1, 'S': 1},  # Position 3 (4th letter)
        {'E': 3, 'Y': 1, 'D': 1}  # Position 4 (5th letter)
    ]

    def __init__(self):
        super().__init__()
        with open("wordle_valid_answers.txt", "r") as f:
            self.actual_guesses = set(f.read().splitlines())

    def guess(self, wordle_state: WordleState, guessable_words: set[str]) -> str:
        if VERBOSE:
            print("\nSTATE :\n"+ str(wordle_state))
        valid_words = [word for word in guessable_words if self.is_valid_word(wordle_state, word.casefold())]
        eliminating_words = [word for word in guessable_words if
                             self.is_valid_word(wordle_state, word.casefold(), ignore_green_letters=True)]

        valid_letter_counts = Counter(letter for word in guessable_words for letter in word)
        actual_letter_counts = Counter(letter for word in self.actual_guesses for letter in word)
        if len(valid_words) > 10:
            guess_words = eliminating_words
            guess_counts = valid_letter_counts
        else:
            guess_words = valid_words
            guess_counts = actual_letter_counts

        # Find the best guess
        best_guess, score, num_valid_words = self.find_best_guess(guess_words, guess_counts)
        if VERBOSE:
            print("Best guess:", best_guess, "Score:", score, "Valid words:", num_valid_words)
        return best_guess

    @staticmethod
    def is_valid_word(state: WordleState, word: str, ignore_green_letters=False) -> bool:
        word = word.upper()
        if not ignore_green_letters:
            for i in range(5):
                if state.green_letters[i] != "_" and word[i] != state.green_letters[i]:
                    return False

        if any(letter in state.gray_letters for letter in word):
            return False

        for i, banned_letters in enumerate(state.yellow_positions):
            if word[i] in banned_letters:
                return False
            if banned_letters and not any(letter in word for letter in banned_letters):
                return False

        return True

    def score_word(self, word, letter_counts):
        """Scores a word based on letter frequency, uniqueness, and common letter placements"""
        unique_letters = set(word)
        base_score = sum(letter_counts[letter] for letter in unique_letters) - len(unique_letters) - 5

        # Apply positional bonuses
        positional_bonus = sum(self.POSITIONAL_BONUSES[i].get(letter.upper(), 0) for i, letter in enumerate(word))

        return base_score + positional_bonus

    def find_best_guess(self, valid_words, letter_counts) -> tuple[str, int, int]:
        """Finds the best next word to guess based on letter frequency and coverage."""
        if not valid_words:
            return "", 0, 0

        # Sort valid words based on score
        ranked_words = sorted(valid_words, key=lambda word: self.score_word(word, letter_counts), reverse=True)
        guess = ranked_words[0]

        return guess, self.score_word(guess, letter_counts), len(valid_words)


if __name__ == "__main__":
    valid_words, guessable_words = load_word_lists(
        word_list_path="wordle_words.txt",
        guessable_word_path="wordle_valid_answers.txt"
    )

    wordle_state = WordleState()
    game = WordleGame(wordle_state, list(valid_words))
    bot = SimonBot()
    rounds_taken = game.bot_play(bot)
    print(f"Rounds taken: {rounds_taken}")
