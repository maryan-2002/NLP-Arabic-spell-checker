# -*- coding: utf8 -*-
import tkinter as tk
from tkinter import messagebox
import codecs
import collections
import re
import time
from nltk.util import ngrams
from nltk.probability import ConditionalFreqDist
from transformers import BertTokenizer, BertForMaskedLM
import torch
import transformers
transformers.logging.set_verbosity_error()  # Show only errors, no warnings
start_time = time.time()


# Matches one or more Arabic characters, including diacritics, in the input text.
def words(text):
    return re.findall(r'[\u0621-\u063A\u0640-\u065E]+', text)


def train(features):
    model = collections.defaultdict(lambda: 1)
    for f in features:
        model[f] += 1
    return model


# Extract Arabic diacritic marks and the Kashida symbol from Arabic text strings
tmp1 = re.compile(r'[\u064B-\u065F\u0640]+', re.UNICODE)

# Open 'arabic.txt' and read its contents as a string.
with codecs.open('arabic.txt', 'r', encoding='utf-8') as f:
    words_list = [tmp1.sub('', word2) for word2 in words(f.read())]
    NWORDS = train(words_list)

# Build a bigram and trigram model
bigrams = list(ngrams(words_list, 2))
trigrams = list(ngrams(words_list, 3))
bigram_freq = ConditionalFreqDist(bigrams)
trigram_freq = ConditionalFreqDist((a, (b, c)) for a, b, c in trigrams)

alphabet = (u'\u0621\u0622\u0623\u0624\u0625\u0626\u0627\u0628\u0629\u062a\u062b\u062c\u062d\u062e\u062f\u0630\u0631'
            u'\u0632\u0633\u0634\u0635\u0636\u0637\u0638\u0639\u063a\u0640\u0641\u0642\u0643\u0644\u0645\u0646\u0647'
            u'\u0648\u0649\u064a')


def edits1(word):
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [a + b[1:] for a, b in splits if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b) > 1]
    replaces = [a + c + b[1:] for a, b in splits for c in alphabet if b]
    inserts = [a + c + b for a, b in splits for c in alphabet]
    return set(deletes + transposes + replaces + inserts)


def known_edits2(word):
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in NWORDS)


def known(words):
    return set(w for w in words if w in NWORDS)


def sequence_score(seq):
    score = 0
    for i in range(len(seq)):
        if i == 0:
            score += NWORDS[seq[i]]
        elif i == 1:
            score += bigram_freq[seq[i - 1]][seq[i]]
        else:
            score += trigram_freq[seq[i - 2], seq[i - 1]][seq[i]]
    return score


def sequence_score(seq):
    score = 0
    for i in range(len(seq)):
        if i == 0:
            # Add a significant weight to the frequency of the word in the dictionary
            score += NWORDS[seq[i]] * 10
        elif i == 1:
            score += bigram_freq[seq[i - 1]][seq[i]]
        else:
            score += trigram_freq[seq[i - 2], seq[i - 1]][seq[i]]
    return score


def beam_search(words, beam_width=3):
    sequences = [([], 0)]
    for word in words:
        all_candidates = []
        for seq, score in sequences:
            candidates = known([word]) or known(edits1(word)) or known_edits2(word) or [word]
            for candidate in candidates:
                # Incorporate the frequency of the candidate into the score
                candidate_score = score + sequence_score(seq + [candidate]) + NWORDS[candidate] * 10
                all_candidates.append((seq + [candidate], candidate_score))
        # Sort the candidates by the updated score which includes frequency
        ordered = sorted(all_candidates, key=lambda x: x[1], reverse=True)
        sequences = ordered[:beam_width]
    return sequences[0][0]


def correct_sentence(sentence):
    original_words = words(sentence)
    corrected_words = beam_search(original_words)
    corrected_sentence = ' '.join(corrected_words)
    return corrected_sentence, corrected_words, original_words


# Load pre-trained BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('asafaya/bert-base-arabic')
model = BertForMaskedLM.from_pretrained('asafaya/bert-base-arabic')


def correct_with_bert(text):
    tokens = tokenizer.tokenize(text)
    inputs = tokenizer.encode(text, return_tensors='pt')
    with torch.no_grad():
        outputs = model(inputs, labels=inputs)
        loss, prediction_scores = outputs[:2]
    predicted_ids = torch.argmax(prediction_scores, dim=-1)
    predicted_text = tokenizer.decode(predicted_ids[0], skip_special_tokens=True)
    return predicted_text


# GUI Part
def correct_and_display_sentence():
    input_sentence = sentence_entry.get()
    if not input_sentence:
        messagebox.showwarning("Warning", "Please enter a sentence.")
        return

    corrected_sentence, corrected_words, original_words = correct_sentence(input_sentence)
    final_correction = correct_with_bert(corrected_sentence)

    corrected_label.config(text="Corrected Sentence: " + final_correction)
    update_frequency_display(original_words, corrected_words)


def update_frequency_display(original_words, corrected_words):
    frequency_frame.pack(pady=10)
    for widget in frequency_frame.winfo_children():
        widget.destroy()

    for original, corrected in zip(original_words, corrected_words):
        if original != corrected:
            frequency = NWORDS.get(corrected, 0)
            freq_text = f"'{corrected}' (corrected from '{original}'): Frequency = {frequency}"
            label = tk.Label(frequency_frame, text=freq_text)
            label.pack()


root = tk.Tk()
root.title("Arabic Sentence Corrector")

input_frame = tk.Frame(root)
input_frame.pack(pady=10)

sentence_label = tk.Label(input_frame, text="Enter a sentence:")
sentence_label.pack(side=tk.LEFT)

sentence_entry = tk.Entry(input_frame, width=50)
sentence_entry.pack(side=tk.LEFT)

correct_button = tk.Button(root, text="Correct Sentence", command=correct_and_display_sentence)
correct_button.pack(pady=10)

corrected_label = tk.Label(root, text="Corrected Sentence: ")
corrected_label.pack(pady=10)

frequency_frame = tk.Frame(root)

root.mainloop()
