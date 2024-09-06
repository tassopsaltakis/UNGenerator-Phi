# UNGenerator-Phi

UNGenerator-Phi is a customizable username generator that allows users to generate unique usernames based on specific criteria. Powered by **Microsoft Phi 3.5**, the application provides options to generate usernames with fantasy, futuristic, or funny themes, as well as the ability to include numbers. It also supports real-time validation and refinement of generated usernames to meet the user's requirements.

## Features

- **Customizable Themes**: Choose between Fantasy, Futuristic, and Funny themes to customize the username generation.
- **Include Numbers Option**: Decide whether the generated usernames should include numbers.
- **Username Length Selection**: Specify the exact length of the username you want to generate.
- **Real-time Validation**: The program validates usernames to ensure they meet the criteria and refines them if necessary.
- **Debug Output**: View the real-time generation process, including the prompt used and the validation results.
- **Responsive Interface**: The application’s interface remains responsive thanks to threaded username generation.

## Requirements

- **Python 3.8+**
- **Llama-cpp** (for loading the Microsoft Phi 3.5 model)
- **Tkinter** (for the GUI)
- **Webbrowser**, **Regex**, and **Pathlib** libraries

You can install these using `pip`