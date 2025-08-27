import dataclasses
import enum
from typing import Self

ALL_WORDS_PATH = "wordle_valid_submissions.txt"
ALL_ANSWERS_PATH = "wordle_correct_answers.txt"
ENGLISH_WORDS_PATH = "english_wordle_words.txt"  # Currently unused


class WordleColor(enum.StrEnum):
    GREEN = "green"
    YELLOW = "yellow"
    GRAY = "gray"

    @classmethod
    def from_str(cls, colors_str: str) -> list[Self]:
        """Given a string of letters representing colors, return a list of WordleColor objects"""
        color_representations = {
            "g": cls.GREEN,
            "y": cls.YELLOW,
            "r": cls.GRAY,
        }
        return [color_representations[c.lower()] for c in colors_str]


@dataclasses.dataclass(frozen=True, kw_only=True)
class WordleGuessResult:
    guess: str
    colors: list[WordleColor]

    def validate(self, num_letters):
        if len(self.guess) != num_letters:
            raise ValueError(f"Invalid guess length: {len(self.guess)}")
        if len(self.colors) != num_letters:
            raise ValueError(f"Invalid number of resulting colors: {len(self.guess)}")

    @classmethod
    def from_strings(cls, word: str, color_str: str) -> Self:
        inst = WordleGuessResult(
            guess=word.upper(),
            colors=WordleColor.from_str(color_str)
        )
        return inst


@dataclasses.dataclass(kw_only=True)
class WordleState:
    green: list[str] = None
    yellow: list[list[str]] = None
    gray: list[str] = None
    num_letters: int = 5
    round: int = 0
    total_rounds: int = 6

    def __post_init__(self):
        # Initialize all the empty lists for tracking
        self.green = ["_"] * self.num_letters
        self.yellow = [[] for _ in range(self.num_letters)]
        self.gray = []

    def update(self, guess: WordleGuessResult):
        """Update the WordleState with the information from a given guess"""
        # Ensure guess is valid length
        guess.validate(self.num_letters)

        # Add each letter in the guess to its corresponding tracking list
        for i, (letter, color) in enumerate(zip(guess.guess, guess.colors)):
            if color == WordleColor.GREEN:
                self.green[i] = letter
            elif color == WordleColor.YELLOW:
                self.yellow[i].append(letter)
            elif color == WordleColor.GRAY:
                self.gray.append(letter)

        self.round += 1

    def check_possible_answer(self, answer: str) -> bool:
        """Check if a given answer could be correct based on the current state"""
        for i, letter in enumerate(answer):
            letter = letter.upper()
            if self.green[i] not in ("_", letter):
                # Doesn't match green letter
                return False
            if letter in self.yellow[i]:
                # Uses a letter in a yellow position
                return False
            if letter in self.gray and letter not in self.green:
                # Uses an invalid (gray) letter
                return False
        return True

    def __str__(self):
        state_display = f"=== TURN {self.round}/{self.total_rounds} ===\n"
        state_display += f"GREEN: {''.join(self.green)}\n"
        state_display += f"YELLOW: {', '.join([''.join(s) for s in self.yellow])}\n"
        state_display += f"GRAY: {''.join(self.gray)}\n"
        state_display += "================"
        return state_display


class WordleSolver:
    def __init__(self, state: WordleState):
        self.state = state
        self.valid_submissions: set | None = None
        self.valid_answers: set | None = None
        self.remaining_answers: list | None = None

        # Load word files and initialize variables
        self.load_files()

        # Reset remaining answers to include all answers
        self.remaining_answers = list(self.valid_answers)

    def load_files(self):
        with open(ALL_WORDS_PATH, "r") as f:
            self.valid_submissions = set(line.strip() for line in f.readlines())
        with open(ALL_ANSWERS_PATH, "r") as f:
            self.valid_answers = set(line.strip() for line in f.readlines())

    def update_remaining_answers(self):
        self.remaining_answers = [word for word in self.remaining_answers if self.state.check_possible_answer(word)]

    def get_best_answers(self, num_results: int):
        sorted_results = sorted(self.remaining_answers, key=get_word_heuristic_score, reverse=True)
        return sorted_results[:num_results]


def get_word_heuristic_score(word: str) -> float:
    letter_frequency_order = "etaoinsrhdlucmfywgpbvkxqjz"
    score = 1
    duplicate_letters = len(word) - len(set(word))
    score -= duplicate_letters / 10

    for letter in word:
        score -= (letter_frequency_order.index(letter) / 1000)

    return score


def handle_user_input(guess_options: list[str], word_length: int) -> tuple[str, str]:
    """Validate and assign word and color strings from user inputs"""
    word, color_input = None, None
    while True:
        try:
            # Get and validate word
            word_input = input("Enter your word (or number): ").strip()
            if len(word_input) <= (len(guess_options) // 10) + 1:
                word = guess_options[int(word_input) - 1]
            elif len(word_input) != word_length:
                raise TypeError(f"Invalid word length: {len(word_input)}")
            else:
                word = word_input

            # Get and validate color string
            color_input = input("Enter your color string: ").strip()
            if len(color_input) != word_length:
                raise TypeError(f"Invalid color string length: {len(color_input)}")
            if not all(c in "ryg" for c in color_input):
                raise TypeError(f"Invalid color string. Please use only 'g', 'y', and 'r'.")

        except (TypeError, IndexError) as e:
            print(e)
            continue

        break

    print(f"({word} -> {color_input})\n")
    return word, color_input


if __name__ == '__main__':
    word_length: int = 5
    num_rounds: int = 6
    state = WordleState()
    solver = WordleSolver(state)
    win = False
    guess_options = []

    for turn in range(num_rounds):
        guess = WordleGuessResult.from_strings(*handle_user_input(guess_options, word_length))
        state.update(guess)
        if "_" not in state.green:
            win = True
            break
        solver.update_remaining_answers()
        print(state)
        print(f"Remaining answers: {len(solver.remaining_answers)}")
        guess_options = solver.get_best_answers(word_length)
        print("\n".join([f"{i+1}. {guess}" for i, guess in enumerate(guess_options)]))

    if win:
        print("You Won!")
    else:
        print("You Lost...")
