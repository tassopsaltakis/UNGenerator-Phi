import tkinter as tk
from tkinter import messagebox
from llama_cpp import Llama
from pathlib import Path
import threading
import re
import webbrowser
import sys
import os
import contextlib
from tkinter import font as tkFont  # Import tkinter font

# Function to suppress stdout and stderr
@contextlib.contextmanager
def suppress_output():
    with open(os.devnull if os.name == 'posix' else 'nul', "w") as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = devnull
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

# Define the correct model path (models directory)
model_dir = Path(__file__).parent / "models"
model_path = model_dir / "phi.gguf"

# Ensure the model file exists
if not model_path.is_file():
    raise FileNotFoundError(f"Model file does not exist at path: {model_path}")

# Load your AI model using llama_cpp with output suppression
with suppress_output():
    model = Llama(model_path=str(model_path))

# Function to open GitHub link
def open_github():
    webbrowser.open("https://github.com/tassopsaltakis")

# Function to validate the generated username
def validate_username(username, length, allow_numbers):
    pattern = "^[A-Za-z"
    if allow_numbers:
        pattern += "0-9"
    pattern += "]{" + str(length) + "}$"
    return re.match(pattern, username) is not None

# Function to refine an invalid username
def refine_username(username, length, allow_numbers):
    allowed_characters = "A-Za-z"
    if allow_numbers:
        allowed_characters += "0-9"
    refined_username = re.sub(f'[^{allowed_characters}]', '', username)
    return refined_username[:length]

# Function to generate a username
def generate_username():
    allow_numbers = number_var.get()
    length = length_var.get()
    fantasy = fantasy_var.get()
    futuristic = futuristic_var.get()
    funny = funny_var.get()

    prompt = f"Generate a unique username for online use that is exactly {length} characters long. "
    prompt += "It may include numbers," if allow_numbers else "It must not include numbers,"
    if fantasy:
        prompt += " The username should have a fantasy theme, like from a mythical world."
    if futuristic:
        prompt += " The username should have a futuristic, sci-fi vibe, something from the future."
    if funny:
        prompt += " Make the username funny, with a playful or humorous twist."
    prompt += " Only respond with the username itself and nothing else."

    try:
        valid_username = False
        while not valid_username:
            debug_text.insert(tk.END, f"Prompt: {prompt}\n")
            with suppress_output():
                response = model(prompt, max_tokens=30)
                username = response['choices'][0]['text'].strip()

            username = username.split(':')[1].strip() if ':' in username else username
            debug_text.insert(tk.END, f"Generated Username (before validation): {username}\n")

            if validate_username(username, length, allow_numbers):
                valid_username = True
                debug_text.insert(tk.END, f"Valid Username: {username}\n")
            else:
                debug_text.insert(tk.END, f"Invalid username: {username}, refining...\n")
                username = refine_username(username, length, allow_numbers)
                debug_text.insert(tk.END, f"Refined Username: {username}\n")
                if validate_username(username, length, allow_numbers):
                    valid_username = True

        root.after(0, lambda: messagebox.showinfo("Generated Username", f"Your username: {username}"))

    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Error", f"An error occurred while generating the username: {e}"))

# Function to handle threading
def threaded_username_generation():
    threading.Thread(target=generate_username).start()

# Setting up the GUI
root = tk.Tk()
root.title("UNGenerator-Phi")
root.geometry("620x600")
root.config(bg="#1F1F1F")  # Dark background

# Load the custom font (e.g., Montserrat)
custom_font_path = Path(__file__).parent / "fonts" / "Montserrat-Regular.ttf"
custom_font = tkFont.Font(family="Montserrat", size=12)

# Variables for checkboxes
number_var = tk.BooleanVar()
length_var = tk.IntVar(value=10)
fantasy_var = tk.BooleanVar()
futuristic_var = tk.BooleanVar()
funny_var = tk.BooleanVar()

# UI elements
tk.Label(root, text="UNGenerator-Phi", font=("Montserrat", 18), bg="#1F1F1F", fg="#FFFFFF").pack(pady=10)

# Debug box
debug_frame = tk.Frame(root, bg="#1F1F1F")
debug_frame.pack(pady=10, padx=20, fill="both", expand=True)

debug_label = tk.Label(debug_frame, text="Debug Output:", anchor="w", bg="#1F1F1F", fg="#FFFFFF", font=custom_font)
debug_label.pack(anchor="w", padx=5)

debug_text = tk.Text(debug_frame, height=10, state="normal", wrap="word", bg="#2E2E2E", fg="#FFFFFF", relief="flat", bd=1, font=custom_font)
debug_text.pack(fill="both", padx=10, pady=5, expand=True)

# Frame for checkboxes
options_frame = tk.Frame(root, bg="#1F1F1F")
options_frame.pack(anchor='w', padx=20, pady=5)

# Checkboxes
tk.Checkbutton(options_frame, text="Include Numbers", variable=number_var, bg="#1F1F1F", fg="#FFFFFF", selectcolor="#2E2E2E", font=custom_font).pack(side="left", padx=5)
tk.Checkbutton(options_frame, text="Fantasy Theme", variable=fantasy_var, bg="#1F1F1F", fg="#FFFFFF", selectcolor="#2E2E2E", font=custom_font).pack(side="left", padx=5)
tk.Checkbutton(options_frame, text="Futuristic Theme", variable=futuristic_var, bg="#1F1F1F", fg="#FFFFFF", selectcolor="#2E2E2E", font=custom_font).pack(side="left", padx=5)
tk.Checkbutton(options_frame, text="Funny Theme", variable=funny_var, bg="#1F1F1F", fg="#FFFFFF", selectcolor="#2E2E2E", font=custom_font).pack(side="left", padx=5)

tk.Label(root, text="Username Length:", font=custom_font, bg="#1F1F1F", fg="#FFFFFF").pack(anchor='w', padx=20, pady=5)
tk.Entry(root, textvariable=length_var, bg="#2E2E2E", fg="#FFFFFF", relief="flat", font=custom_font).pack(anchor='w', padx=20)

# Generate button
tk.Button(root, text="Generate Username", command=threaded_username_generation, bg="#4CAF50", fg="#FFFFFF", relief="flat", font=custom_font).pack(pady=20)

# Footer
footer_frame = tk.Frame(root, bg="#1F1F1F")
footer_frame.pack(side="bottom", fill="x", pady=10)

version_label = tk.Label(footer_frame, text="Version 1.3", anchor="e", bg="#1F1F1F", fg="#FFFFFF", font=custom_font)
version_label.pack(side="right", padx=10)

github_link = tk.Label(footer_frame, text="By: tassopsaltakis", fg="#4CAF50", cursor="hand2", bg="#1F1F1F", font=custom_font)
github_link.pack(side="left", padx=10)
github_link.bind("<Button-1>", lambda e: open_github())

root.mainloop()
