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
    # Construct a regex pattern based on the toggles
    pattern = "^[A-Za-z"  # Start with allowing letters
    if allow_numbers:
        pattern += "0-9"  # Allow numbers if the toggle is on
    pattern += "]{" + str(length) + "}$"  # Enforce the exact length
    return re.match(pattern, username) is not None


# Function to refine an invalid username by stripping invalid characters
def refine_username(username, length, allow_numbers):
    # Build the allowed character set based on toggles
    allowed_characters = "A-Za-z"
    if allow_numbers:
        allowed_characters += "0-9"

    # Remove any characters not in the allowed set
    refined_username = re.sub(f'[^{allowed_characters}]', '', username)

    # Truncate to the required length if necessary
    return refined_username[:length]


# Function to generate a username based on user selections (runs in a separate thread)
def generate_username():
    # Collect checkbox values
    allow_numbers = number_var.get()
    length = length_var.get()

    # Adjust the prompt based on user selection of toggles
    prompt = (
        f"Generate a unique username for online use that is exactly {length} characters long. "
        f"{'It may include numbers,' if allow_numbers else 'It must not include numbers,'} "
        "and it must be creative and pronounceable. Only respond with the username itself and nothing else."
    )

    try:
        valid_username = False
        while not valid_username:
            # Generate a username using the AI model
            debug_text.insert(tk.END, f"Prompt: {prompt}\n")  # Add the prompt to the debug box

            # Suppress Llama output during generation
            with suppress_output():
                response = model(prompt, max_tokens=30)
                username = response['choices'][0]['text'].strip()

            # Extract the first valid word from the response
            username = username.split(':')[1].strip() if ':' in username else username
            debug_text.insert(tk.END, f"Generated Username (before validation): {username}\n")

            # Validate the username
            if validate_username(username, length, allow_numbers):
                valid_username = True
                debug_text.insert(tk.END, f"Valid Username: {username}\n")
            else:
                # Refine the username and attempt to fix it
                debug_text.insert(tk.END, f"Invalid username: {username}, refining...\n")
                username = refine_username(username, length, allow_numbers)
                debug_text.insert(tk.END, f"Refined Username: {username}\n")
                if validate_username(username, length, allow_numbers):
                    valid_username = True

        # Display the validated username in a message box (in the main thread)
        root.after(0, lambda: messagebox.showinfo("Generated Username", f"Your username: {username}"))

    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Error", f"An error occurred while generating the username: {e}"))


# Function to handle threading and keep the GUI responsive
def threaded_username_generation():
    threading.Thread(target=generate_username).start()


# Setting up the GUI
root = tk.Tk()
root.title("UNGenerator-Phi")
root.geometry("600x450")

# Variables for the checkboxes
number_var = tk.BooleanVar()
length_var = tk.IntVar(value=8)  # Default length is 8

# UI elements
tk.Label(root, text="UNGenerator-Phi", font=("Arial", 16)).pack(pady=10)

# Debug box to show the process of generation
debug_frame = tk.Frame(root)
debug_frame.pack(pady=10, padx=20, fill="both", expand=True)

debug_label = tk.Label(debug_frame, text="Debug Output:", anchor="w")
debug_label.pack(anchor="w", padx=5)

debug_text = tk.Text(debug_frame, height=10, state="normal", wrap="word", bg="#f0f0f0", relief="sunken", bd=1)
debug_text.pack(fill="both", padx=10, pady=5, expand=True)

tk.Checkbutton(root, text="Include Numbers", variable=number_var).pack(anchor='w', padx=20)

tk.Label(root, text="Username Length:", font=("Arial", 12)).pack(anchor='w', padx=20, pady=5)
tk.Entry(root, textvariable=length_var).pack(anchor='w', padx=20)

# Generate button (triggers the threaded function)
tk.Button(root, text="Generate Username", command=threaded_username_generation).pack(pady=20)

# Footer with version and GitHub link
footer_frame = tk.Frame(root)
footer_frame.pack(side="bottom", fill="x", pady=10)

version_label = tk.Label(footer_frame, text="Version 1.0", anchor="e")
version_label.pack(side="right", padx=10)

github_link = tk.Label(footer_frame, text="By: tassopsaltakis", fg="blue", cursor="hand2", anchor="w")
github_link.pack(side="left", padx=10)
github_link.bind("<Button-1>", lambda e: open_github())

# Start the GUI loop
root.mainloop()
