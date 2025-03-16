import random
from dataclasses import dataclass, field


@dataclass
class WordleState:
    green_letters: list[str] = field(default_factory=lambda: ["_" for _ in range(5)])
    yellow_positions: list[set[str]] = field(default_factory=lambda: [set() for _ in range(5)])
    gray_letters: set[str] = field(default_factory=set)

    def __str__(self):
        yellow_display = [("".join(sorted(letters)) if letters else "None").ljust(6) + "|" for letters in
                          self.yellow_positions]
        return (
            "========================\n"
            f"Green:  {''.join(letter.upper() if letter else '_' for letter in self.green_letters)}\n"
            f"Yellow: {'  '.join(yellow_display)}\n"
            f"Gray:   {''.join(self.gray_letters) if self.gray_letters else 'None'}\n"
            "========================\n"
        )


class WordleGame:
    def __init__(self, wordle_state: WordleState, guessable_words: list[str], override_word: str | None = None):
        self.state = wordle_state
        self.guessable_words = guessable_words
        self.target_word = override_word.upper() if override_word else random.choice(self.guessable_words).upper()

    def guess(self, word: str) -> bool:
        """Processes a guess and updates the game state. Returns True if the guess is valid, False otherwise."""
        if len(word) != 5 or word not in self.guessable_words:
            return False
        for i, letter in enumerate(word.upper()):
            if letter == self.target_word[i]:
                self.state.green_letters[i] = letter
            elif letter in self.target_word:
                self.state.yellow_positions[i].add(letter)
            else:
                self.state.gray_letters.add(letter)
        return True

    def human_play(self, max_attempts=6) -> int:
        attempts = 0
        while attempts < max_attempts:
            print(self.state)
            print("(Type 'quit' or 'exit' to quit)")
            guess = input("Enter your guess: ").casefold()

            if guess in ("quit", "exit"):
                print("See you next time!")
                return -1

            if not self.guess(guess):
                print("Invalid guess. Try again.\n")
                continue
            attempts += 1

            if guess.casefold() == self.target_word.casefold():
                print(f"\n\n'{self.target_word.upper()}' is correct! You win!")
                return attempts

        print("\n\nYou lost! The correct word was '" + self.target_word.upper() + "'")
        print("Final State:\n" + str(self.state))

    def bot_play(self, bot, max_attempts=6) -> int:
        attempts = 0
        while attempts < max_attempts:
            # Allow the bot to make a guess
            guess = bot.guess(self.state, self.guessable_words).casefold()

            if not self.guess(guess):
                print("BOT GUESS INVALID. TRY AGAIN.\n")
                return -1

            attempts += 1

            if guess.casefold() == self.target_word.casefold():
                print(f"\n\n'{self.target_word.upper()}' is correct! You win!")
                return attempts

        print("\n\nYou lost! The correct word was '" + self.target_word.upper() + "'")


def load_word_lists(word_list_path, guessable_word_path):
    with open(word_list_path, "r") as f:
        words = f.read().splitlines()
    with open(guessable_word_path, "r") as f:
        guessable_words = f.read().splitlines()
    return set(words), set(guessable_words)


if __name__ == "__main__":
    valid_words, guessable_words = load_word_lists(
        word_list_path="wordle_words.txt",
        guessable_word_path="wordle_valid_answers.txt"
    )

    wordle_state = WordleState()
    game = WordleGame(wordle_state, list(valid_words))
    rounds_taken = game.human_play()
    if rounds_taken != -1:
        print(f"Rounds taken: {rounds_taken}")
