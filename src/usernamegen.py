import tkinter as tk
from tkinter import messagebox
from gpt4all import GPT4All
from pathlib import Path
import threading
import re  # For regex validation

# Define the correct model path (models directory)
model_dir = Path(__file__).parent / "models"
model_path = model_dir / "phi.gguf"

# Ensure the correct model path is printed for debugging purposes
print(f"Model Path: {model_path}")

# Ensure the model file exists
if not model_path.is_file():
    raise FileNotFoundError(f"Model file does not exist at path: {model_path}")

# Load your AI model using the directory, but pass the model name without extension
model = GPT4All(model_name="phi", model_path=str(model_dir), allow_download=False)


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
            print(f"Prompt: {prompt}")  # Debug the prompt being sent
            username = model.generate(prompt, n_predict=30).strip()

            # Extract the first valid word from the response (ignore things like "solution:")
            username = username.split(':')[1].strip() if ':' in username else username
            print(f"Generated Username (before validation): {username}")

            # Validate the username
            if validate_username(username, length, allow_numbers):
                valid_username = True
            else:
                # Refine the username and attempt to fix it
                print(f"Invalid username: {username}, refining...")
                username = refine_username(username, length, allow_numbers)
                print(f"Refined Username: {username}")
                if validate_username(username, length, allow_numbers):
                    valid_username = True

        print(f"Valid Username: {username}")  # Debug the validated username

        # Display the validated username in a message box (in the main thread)
        root.after(0, lambda: messagebox.showinfo("Generated Username", f"Your username: {username}"))

    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Error", f"An error occurred while generating the username: {e}"))


# Function to handle threading and keep the GUI responsive
def threaded_username_generation():
    threading.Thread(target=generate_username).start()


# Setting up the GUI
root = tk.Tk()
root.title("Username Generator")
root.geometry("400x300")

# Variables for the checkboxes
number_var = tk.BooleanVar()
length_var = tk.IntVar(value=8)  # Default length is 8

# UI elements
tk.Label(root, text="Username Generator", font=("Arial", 16)).pack(pady=10)

tk.Checkbutton(root, text="Include Numbers", variable=number_var).pack(anchor='w', padx=20)

tk.Label(root, text="Username Length:", font=("Arial", 12)).pack(anchor='w', padx=20, pady=5)
tk.Entry(root, textvariable=length_var).pack(anchor='w', padx=20)

# Generate button (triggers the threaded function)
tk.Button(root, text="Generate Username", command=threaded_username_generation).pack(pady=20)

# Start the GUI loop
root.mainloop()
