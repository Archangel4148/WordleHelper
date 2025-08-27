
# Just a quick script to get letter frequencies and position frequencies from the valid answers list

with open("resources/wordle_correct_answers.txt", "r") as f:
    all_words = [line.strip() for line in f.readlines()]

word_count = len(all_words)
alphabet = "abcdefghijklmnopqrstuvwxyz"
full_counts = {l: 0 for l in alphabet}
pos_counts = [[0] * 5 for _ in range(26)]

for word in all_words:
    for i, letter in enumerate(word):
        full_counts[letter] += 1
        pos_counts[alphabet.index(letter)][i] += 1

frequencies = {alpha: [v / word_count for v in count] for alpha, count in zip(alphabet, pos_counts)}
print(frequencies)

with open("resources/position_frequencies.txt", "w") as f:
    f.write(f"{''.join(sorted(full_counts, key=lambda i: full_counts[i], reverse=True))}\n")
    for letter, freq in frequencies.items():
        f.write(f"{letter} : {', '.join([str(f) for f in freq])}\n")
