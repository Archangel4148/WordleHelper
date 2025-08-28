import time
from collections import Counter


def get_result(answer: str, guess: str) -> str:
    """Get the resulting color string for a given guess/answer pair"""
    assert(len(answer) == len(guess))
    answer_chars = list(answer)
    # All gray by default
    colors = ["r"] * len(answer)

    # Pass 1 - Mark and remove greens
    for i, (al, gl) in enumerate(zip(answer, guess)):
        if gl == al:
            colors[i] = "g"
            answer_chars[i] = "_"

    # Pass 2 - Mark yellows
    for i, (al, gl) in enumerate(zip(answer_chars, guess)):
        if gl in answer_chars:
            colors[i] = "y"
            guess_idx = answer_chars.index(gl)
            answer_chars[guess_idx] = "_"

    return "".join(colors)


possible_words = ["cat", "rat", "arc", "zen"]
answer = "rat"

result_groups = {guess: {} for guess in possible_words}

# For each guess, group possible answers by their resulting pattern
for guess in possible_words:
    for theoretical_answer in possible_words:
        result = get_result(theoretical_answer, guess)
        result_groups[guess].setdefault(result, [])
        result_groups[guess][result].append(theoretical_answer)

# Find the probability of each pattern
result_probabilities = {r: {k: 0 for k in d} for r, d in result_groups.items()}

for word, d in result_groups.items():
    print(word, "-", d)




