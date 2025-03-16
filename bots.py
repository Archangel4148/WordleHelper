class WordleBot:
    pass

# MIGRATING STUFF:

# POSITIONAL_BONUSES = [
#     {'A': 2, 'S': 1, 'T': 1},  # Position 0 (1st letter)
#     {'R': 2, 'O': 1, 'T': 1},  # Position 1 (2nd letter)
#     {'I': 2, 'E': 1, 'N': 1},  # Position 2 (3rd letter)
#     {'E': 2, 'A': 1, 'S': 1},  # Position 3 (4th letter)
#     {'E': 3, 'Y': 1, 'D': 1}  # Position 4 (5th letter)
# ]

# class WordleSolver:
#     def __init__(self, wordle_state: WordleState, all_valid_words: set[str], guessable_words: set[str]):
#         self.state = wordle_state
#         self.all_valid_words = all_valid_words
#         self.guessable_words = guessable_words
#
#         self.valid_letter_counts: Counter | None = None
#         self.guess_letter_counts: Counter | None = None
#
#         self.get_letter_counts()
#
#     def get_letter_counts(self):
#         self.valid_letter_counts = Counter(letter for word in self.all_valid_words for letter in word)
#         self.guess_letter_counts = Counter(letter for word in self.guessable_words for letter in word)
#
#     def get_valid_words(self) -> list[str]:
#         return [word for word in self.all_valid_words if self.is_valid_word(word)]
#
#     def get_eliminating_words(self) -> list[str]:
#         """Returns a list of valid words, ignoring green letters to better eliminate possible letters"""
#         return [word for word in self.all_valid_words if self.is_valid_word(word, ignore_green_letters=True)]
#     def is_valid_word(self, word: str, ignore_green_letters=False) -> bool:
#         if not ignore_green_letters:
#             for i in range(5):
#                 if self.state.green_letters[i] != "_" and word[i] != self.state.green_letters[i]:
#                     return False
#
#         if any(letter in self.state.gray_letters for letter in word):
#             return False
#
#         for i, banned_letters in enumerate(self.state.yellow_positions):
#             if word[i] in banned_letters:
#                 return False
#             if banned_letters and not any(letter in word for letter in banned_letters):
#                 return False
#
#         return True
#
#     @staticmethod
#     def score_word(word, letter_counts):
#         """Scores a word based on letter frequency, uniqueness, and common letter placements"""
#         unique_letters = set(word)
#         base_score = sum(letter_counts[letter] for letter in unique_letters) - len(unique_letters) - 5
#
#         # Apply positional bonuses
#         positional_bonus = sum(POSITIONAL_BONUSES[i].get(letter.upper(), 0) for i, letter in enumerate(word))
#
#         return base_score + positional_bonus
#
#
#     def find_best_guess(self, result_count: int = 1, actual_guess: bool = False) -> tuple[list[tuple], int]:
#         """Finds the best next word to guess based on letter frequency and coverage."""
#
#         valid_words = self.get_valid_words() if actual_guess else self.get_eliminating_words()
#         letter_counts = self.guess_letter_counts if actual_guess else self.valid_letter_counts
#         if not valid_words:
#             return [], 0
#
#         # Sort valid words based on score
#         ranked_words = sorted(valid_words, key=lambda word: self.score_word(word, letter_counts), reverse=True)
#         best_guesses = ranked_words[:result_count]
#
#         return [(guess, self.score_word(guess, letter_counts)) for guess in best_guesses], len(valid_words)
