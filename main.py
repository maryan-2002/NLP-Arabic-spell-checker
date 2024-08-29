import tkinter as tk
from tkinter import font as tkFont
import subprocess
import os


def on_leven_click():
    script_path = os.path.join(os.path.dirname(__file__), 'levenAlgo.py')
    subprocess.run(["python", script_path])

def on_ngram_click():
    script_path = os.path.join(os.path.dirname(__file__), 'nGrams.py')
    subprocess.run(["python", script_path])


# Create the main window
root = tk.Tk()
root.title("Spell Checker Program")

# Calculate position to center the window on the screen
window_width = 400
window_height = 200
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 2)
root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

# Set the background color for the main window
root.configure(background='light blue')

# Define custom font style for the label
custom_font = tkFont.Font(family="Times New Roman", size=15, weight="bold")

# Create a label for the window with a different background color
welcome_label = tk.Label(root, text="Welcome to our Spell Checker program", bg='light blue', font=custom_font)
welcome_label.pack(pady=20)

# Define button dimensions and styles
button_width = 22
button_height = 2
button_color = 'light gray'
button_foreground = 'black'
custom_font1 = tkFont.Font(family="Times New Roman", size=11, weight="bold")

# Create a button for the Leven algorithm
leven_button = tk.Button(root, text="Levenshtein Distance", command=on_leven_click, width=button_width,
                         height=button_height, bg=button_color, fg=button_foreground, font=custom_font1)
leven_button.pack(pady=10)

# Create a button for n-gram
ngram_button = tk.Button(root, text="n-gram", command=on_ngram_click, width=button_width, height=button_height,
                         bg=button_color, fg=button_foreground, font=custom_font1)
ngram_button.pack(pady=10)

# Start the GUI event loop
root.mainloop()
