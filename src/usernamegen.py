import tkinter as tk
from tkinter import messagebox
from llama_cpp import Llama
from pathlib import Path
import threading
import re  # For regex validation
import webbrowser  # To open GitHub link
import sys
import os
import contextlib  # For suppressing output

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

# Function to validate the generated username based on the toggles
def validate_username(username, length, allow_numbers):
    pattern = "^[A-Za-z"
    if allow_numbers:
        pattern += "0-9"
    pattern += "]{" + str(length) + "}$"
    return re.match(pattern, username) is not None

# Function to refine an invalid username by stripping invalid characters
def refine_username(username, length, allow_numbers):
    allowed_characters = "A-Za-z"
    if allow_numbers:
        allowed_characters += "0-9"

    refined_username = re.sub(f'[^{allowed_characters}]', '', username)
    return refined_username[:length]

# Function to generate a username based on user selections (runs in a separate thread)
def generate_username():
    allow_numbers = number_var.get()
    length = length_var.get()
    fantasy = fantasy_var.get()
    futuristic = futuristic_var.get()
    funny = funny_var.get()

    prompt = (
        f"Generate a unique username for online use that is exactly {length} characters long. "
        f"{'It may include numbers,' if allow_numbers else 'It must not include numbers,'} "
    )
    if fantasy:
        prompt += "The username should have a fantasy theme, like from a mythical world. "
    if futuristic:
        prompt += "The username should have a futuristic, sci-fi vibe. "
    if funny:
        prompt += "Make the username funny, with a humorous twist. "

    prompt += "Only respond with the username itself and nothing else."

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

# Function to handle threading and keep the GUI responsive
def threaded_username_generation():
    threading.Thread(target=generate_username).start()

# Setting up the modern UI
root = tk.Tk()
root.title("UNGenerator-Phi")
root.geometry("620x600")

# Apply modern styling
root.configure(bg="#F0F0F0")
root.option_add("*Font", "Arial 12")
root.option_add("*Button.Background", "#4CAF50")
root.option_add("*Button.Foreground", "white")
root.option_add("*Button.BorderWidth", 0)

# Variables for the checkboxes
number_var = tk.BooleanVar()
length_var = tk.IntVar(value=8)  # Default length is 8
fantasy_var = tk.BooleanVar()
futuristic_var = tk.BooleanVar()
funny_var = tk.BooleanVar()

# UI elements with padding for modern look
tk.Label(root, text="UNGenerator-Phi", font=("Arial", 18, "bold"), bg="#F0F0F0", pady=10).pack()

# Debug box
debug_frame = tk.Frame(root, bg="#F0F0F0")
debug_frame.pack(pady=10, padx=20, fill="both", expand=True)

debug_label = tk.Label(debug_frame, text="Debug Output:", bg="#F0F0F0", anchor="w", padx=10)
debug_label.pack(anchor="w")

debug_text = tk.Text(debug_frame, height=10, wrap="word", bg="#FFF", relief="flat", bd=1)
debug_text.pack(fill="both", padx=10, pady=5, expand=True)

# Create a frame for the checkboxes
options_frame = tk.Frame(root, bg="#F0F0F0")
options_frame.pack(anchor='w', padx=20, pady=5)

# Checkboxes in a row for modern layout
tk.Checkbutton(options_frame, text="Include Numbers", variable=number_var, bg="#F0F0F0").pack(side="left", padx=5)
tk.Checkbutton(options_frame, text="Fantasy Theme", variable=fantasy_var, bg="#F0F0F0").pack(side="left", padx=5)
tk.Checkbutton(options_frame, text="Futuristic Theme", variable=futuristic_var, bg="#F0F0F0").pack(side="left", padx=5)
tk.Checkbutton(options_frame, text="Funny Theme", variable=funny_var, bg="#F0F0F0").pack(side="left", padx=5)

tk.Label(root, text="Username Length:", font=("Arial", 12), bg="#F0F0F0").pack(anchor='w', padx=20, pady=5)
tk.Entry(root, textvariable=length_var, relief="flat", bd=1).pack(anchor='w', padx=20, pady=5)

# Generate button
tk.Button(root, text="Generate Username", command=threaded_username_generation, padx=20, pady=10).pack(pady=20)

# Footer with version and GitHub link
footer_frame = tk.Frame(root, bg="#F0F0F0")
footer_frame.pack(side="bottom", fill="x", pady=10)

version_label = tk.Label(footer_frame, text="Version 1.3", anchor="e", bg="#F0F0F0")
version_label.pack(side="right", padx=10)

github_link = tk.Label(footer_frame, text="By: tassopsaltakis", fg="blue", cursor="hand2", bg="#F0F0F0", anchor="w")
github_link.pack(side="left", padx=10)
github_link.bind("<Button-1>", lambda e: open_github())

# Start the GUI loop
root.mainloop()
