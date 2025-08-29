import dataclasses
import enum
from typing import Self

from info_theory_stuff import get_info_gain

ALL_WORDS_PATH = "resources/wordle_valid_submissions.txt"
ALL_ANSWERS_PATH = "resources/wordle_correct_answers.txt"
BACKUP_WORDS_PATH = "resources/other_dataset_words.txt"
POSITION_FREQUENCIES_PATH = "resources/position_frequencies.txt"


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
    round: int = 1
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

        all_yellow_letters = set(c for l in self.yellow for c in l)
        for letter in all_yellow_letters:
            if letter.lower() not in answer:
                # Does not contain a required yellow letter
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

        # Pre-processed word storage
        self.sorted_submissions: list | None = None
        self.word_scores: dict[str, float] = {}

        # Guess tracking variable
        self.remaining_answers: list | None = None

        # Backup guess tracking variables
        self.backup_guesses: set | None = None
        self.backup_flag: bool = False

        # Letter frequencies
        self.letter_frequency_order: dict[str, int] = {}
        self.position_frequencies: dict[str, list[float]] = {}

        # Load word files and initialize variables
        self.load_files()

        # Reset remaining answers to include all answers
        self.remaining_answers = list(self.valid_answers)

    def load_files(self):
        with open(POSITION_FREQUENCIES_PATH, "r") as f:
            # Parse position frequencies from file
            lines = f.readlines()
            self.letter_frequency_order = {l: i for i, l in enumerate(lines.pop(0).strip())}
            for line in lines:
                sections = line.split(" : ")
                letter = sections[0]
                values = [float(v) for v in sections[1].split(", ")]
                self.position_frequencies[letter] = values
        with open(ALL_WORDS_PATH, "r") as f:
            self.valid_submissions = set(line.strip() for line in f.readlines())
            self.word_scores = {word: self.get_word_heuristic_score(word) for word in self.valid_submissions}
            self.sorted_submissions = sorted(self.valid_submissions, key=lambda w: self.word_scores[w], reverse=True)
        with open(ALL_ANSWERS_PATH, "r") as f:
            self.valid_answers = set(line.strip() for line in f.readlines())
        with open(BACKUP_WORDS_PATH, "r") as f:
            self.backup_guesses = set(line.strip() for line in f.readlines())

    def update_remaining_answers(self):
        self.remaining_answers = [word for word in self.remaining_answers if self.state.check_possible_answer(word)]

        if len(self.remaining_answers) == 0 and not self.backup_flag:
            # Re-search using the backup guesses
            self.remaining_answers = [word for word in self.backup_guesses if self.state.check_possible_answer(word)]
            self.backup_flag = True

    def get_best_answers(self, num_results: int, candidate_depth: int):
        # Find the "best" candidates using a simple heuristic
        heuristic_guess_candidates = self.sorted_submissions[:candidate_depth]
        heuristic_answer_candidates = sorted(self.remaining_answers, key=lambda w: self.word_scores[w], reverse=True)[
            :candidate_depth]
        candidates = set(heuristic_guess_candidates) | set(heuristic_answer_candidates)

        # Focus on the candidates and find the best information gain
        info_guesses, info_answers = [], []
        for g in candidates:
            info = get_info_gain(g, self.remaining_answers)
            if g in self.remaining_answers:
                info_answers.append((g, info))
            else:
                info_guesses.append((g, info))

        # Sort lists by descending information gain
        best_answers = sorted(info_answers, key=lambda g: g[1], reverse=True)
        best_guesses = sorted(info_guesses, key=lambda g: g[1], reverse=True)

        return best_answers[:num_results], best_guesses[:num_results]

    def get_word_heuristic_score(self, word: str) -> float:
        score = 1
        duplicate_letters = len(word) - len(set(word))
        score -= duplicate_letters / 10

        for i, letter in enumerate(word):
            score -= (self.letter_frequency_order[letter] / 1000)
            score += self.position_frequencies[letter][i]

        return score


def handle_user_input(guess_options: list[str], word_length: int) -> tuple[str, str]:
    """Validate and assign word and color strings from user inputs"""
    word, color_input = None, None
    while True:
        try:
            # Get and validate word
            word_input = input("\nEnter your word (or number): ").strip()
            if len(word_input) <= (len(guess_options) // 10) + 1:
                try:
                    word = guess_options[int(word_input) - 1]
                except (IndexError, ValueError):
                    raise IndexError(f"Invalid guess list selection: '{word_input}'")
            elif len(word_input) != word_length:
                raise ValueError(f"Invalid word length: {len(word_input)}")
            else:
                word = word_input

            # Get and validate color string
            color_input = input("Enter your color string: ").strip()
            if len(color_input) != word_length:
                raise ValueError(f"Invalid color string length: {len(color_input)}")
            if not all(c in "ryg" for c in color_input):
                raise ValueError(f"Invalid color string. Please use only 'g', 'y', and 'r'.")

        except (ValueError, IndexError) as e:
            print(e)
            continue

        break

    print(f"({word} -> {color_input})\n")
    return word, color_input


def main():
    # User inputs
    word_length: int = 5  # Number of letters in each word
    num_rounds: int = 6  # Number of guesses allowed
    num_recommendations: int = 5  # Number of recommended guesses/answers to display
    candidate_depth: int = 200  # Number of candidates to deep-search (this affects runtime!)

    # Game variables
    state = WordleState()
    solver = WordleSolver(state)
    win = False

    for turn in range(num_rounds):
        # Display the game state and answer recommendations
        print(state)
        if solver.backup_flag:
            print("-- USING BACKUP ANSWERS! --")
        print(f"Remaining answers: {len(solver.remaining_answers)}")
        best_answers, best_guesses = solver.get_best_answers(num_recommendations, candidate_depth)
        print("Best Information guesses:")
        print("\n".join([f"{i + 1}. {guess[0]} ({guess[1]})" for i, guess in enumerate(best_guesses)]))
        print("Best Answers:")
        print("\n".join(
            [f"{i + 1 + num_recommendations}. {guess[0]} ({guess[1]})" for i, guess in enumerate(best_answers)])
        )

        # Get user's guess and update the state
        guess_options = [g[0] for g in best_guesses + best_answers]
        guess = WordleGuessResult.from_strings(*handle_user_input(guess_options, word_length))
        state.update(guess)

        # Check for a win
        if "_" not in state.green:
            win = True
            break

        # Update the solver's recommendations
        solver.update_remaining_answers()

    if win:
        print("You Won!")
    else:
        print("You Lost...")


if __name__ == '__main__':
    main()
