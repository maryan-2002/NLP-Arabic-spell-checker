import tkinter as tk
from tkinter import filedialog, messagebox


def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def find_best_matches(misspelled_word, dictionary):
    best_matches = []
    for word in dictionary:
        distance = levenshtein_distance(misspelled_word, word)
        if len(best_matches) < 3:
            best_matches.append((word, distance))
            best_matches.sort(key=lambda x: x[1])  # Keep list sorted by distance
        elif distance < best_matches[-1][1]:  # Compare with the largest distance in the list
            best_matches[-1] = (word, distance)
            best_matches.sort(key=lambda x: x[1])  # Re-sort list
    return best_matches


def load_dictionary(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        words = file.read().split()
    return words


def update_sentence(word, replacement):
    current_text = sentence_entry.get()
    new_text = current_text.replace(word, replacement)
    sentence_entry.delete(0, tk.END)
    sentence_entry.insert(0, new_text)
    corrected_label.config(text="Corrected Sentence: " + new_text)


def correct_input_sentence():
    input_sentence = sentence_entry.get()
    if not input_sentence:
        messagebox.showwarning("Warning", "Please enter a sentence.")
        return

    # Clear all children from the suggestions_frame before adding new suggestions
    for widget in suggestions_frame.winfo_children():
        widget.destroy()

    suggestions_frame.pack(pady=10)  # Ensure the frame is packed

    words = input_sentence.split()
    for word in words:
        best_matches = find_best_matches(word, correct_words)
        if best_matches[0][1] > 0:  # If the smallest distance is greater than 0
            # Create a frame for each word's suggestions
            word_frame = tk.Frame(suggestions_frame)
            word_frame.pack(fill='x', expand=True)  # Pack the frame to expand in the x direction

            # Create a label for the current word
            label = tk.Label(word_frame, text=f"Top 3 word match <{word}>:")
            label.pack(side=tk.LEFT)

            # Create a button for each match in the current word's frame
            for index, match in enumerate(best_matches):
                btn_text = f"{index + 1}: {match[0]}"
                btn = tk.Button(word_frame, text=btn_text,
                                command=lambda m=match[0], w=word: update_sentence(w, m))
                btn.pack(side=tk.LEFT, padx=2)


# Load the dictionary
dictionary_file = 'Arabic_spell-checking_dictionary.txt'  # Update this path
correct_words = load_dictionary(dictionary_file)

# Count the number of words
word_count = len(correct_words)
print(f"Number of words in the dictionary: {word_count}")

# GUI part
root = tk.Tk()
root.title("Arabic Spell Checker")
input_frame = tk.Frame(root)
input_frame.pack(pady=10)
sentence_label = tk.Label(input_frame, text="Enter a sentence:")
sentence_label.pack(side=tk.LEFT)
sentence_entry = tk.Entry(input_frame, width=50)
sentence_entry.pack(side=tk.LEFT)
correct_button = tk.Button(root, text="Check Sentence", command=correct_input_sentence)
correct_button.pack(pady=10)
corrected_label = tk.Label(root, text="Corrected: ")
corrected_label.pack(pady=10)
suggestions_frame = tk.Frame(root)
root.mainloop()
