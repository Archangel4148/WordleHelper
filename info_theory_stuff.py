import math


def get_result(answer: str, guess: str) -> str:
    """Get the resulting color string for a given guess/answer pair"""
    assert (len(answer) == len(guess))
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


def get_info_gain(guess: str, possible_answers: list[str]) -> float:
    """Calculate the information gained (in bits) from a given guess"""
    num_answers = len(possible_answers)
    if num_answers == 0:
        return 0.0

    # Group possible answers by their resulting pattern
    result_groups = {}
    for theoretical_answer in possible_answers:
        result = get_result(theoretical_answer, guess)
        result_groups.setdefault(result, []).append(theoretical_answer)

    current_entropy = math.log2(num_answers)
    expected_entropy = 0.0
    for result, matches in result_groups.items():
        num_matches = len(matches)

        # Calculate probability/entropy for each result
        prob = num_matches / num_answers
        entropy = math.log2(num_matches)

        # Update total guess entropy
        expected_entropy += prob * entropy

    # Calculate total guess entropy and information gain
    information_gain = current_entropy - expected_entropy

    return information_gain


if __name__ == '__main__':
    possible_words = [
        "plumb",
        "crane",
        "flame",
        "grape",
        "bland",
        "slate",
        "spike",
        "trout",
        "zebra",
        "fjord"
    ]
    best_guess = max(possible_words, key=lambda g: get_info_gain(g, possible_words))
    print("Best guess:", best_guess)
