from wordle_tools import WordleState, WordleSolver, load_word_lists, WordleGame

PRINT_VALID_WORDS = False
VERBOSE = True


def print_v(*args, **kwargs):
    if VERBOSE:
        print(*args, **kwargs)


if __name__ == "__main__":
    # Define the game state and create a solver
    wordle_state = WordleState()
    all_valid_words, guessable_words = load_word_lists("wordle_words.txt", "wordle_valid_answers.txt")
    # solver = WordleSolver(wordle_state, all_valid_words, guessable_words)

    # Create a game to feed guesses into
    game = WordleGame(wordle_state, list(all_valid_words))

    # Solve the game and output the results
    valid_words = solver.get_valid_words()

    if valid_words:
        if PRINT_VALID_WORDS:
            print_v("Valid Words:")
            sorted_words = sorted(
                valid_words, key=lambda word: solver.score_word(word, solver.valid_letter_counts), reverse=True
            )
            scored_words = [(word, int(solver.score_word(word, solver.valid_letter_counts))) for word in sorted_words]
            for word, score in scored_words:
                print(f"{word} ({score})")

        # Find the best guesses (includes all valid words)
        print_v("\nBest Information Guesses:")
        eliminating_guesses, count = solver.find_best_guess(result_count=1)
        print_v(f"(Found {count} valid words)")
        for i, guess in enumerate(eliminating_guesses):
            print(f"{i + 1}. {guess[0]} ({int(guess[1])})")

        # Find the best English guesses (only English, might be missing some words)
        print_v("\nBest Actual Guesses:")
        actual_guesses, count = solver.find_best_guess(result_count=1, actual_guess=True)
        print_v(f"(Found {count} valid English words)")
        for i, guess in enumerate(actual_guesses):
            print(f"{i + 1}. {guess[0]} ({int(guess[1])})")

        if len(valid_words) > 10:
            # If there are lots of valid words, use the eliminating guess (if there is one)
            guess = eliminating_guesses[0] or actual_guesses[0]
        else:
            # Otherwise, use the best English guess (if there is one)
            guess = actual_guesses[0] or eliminating_guesses[0]




    else:
        print_v("No valid words found.")
