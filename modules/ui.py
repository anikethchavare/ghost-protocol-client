# ghost-protocol-client - modules/ui.py

"""
Copyright 2026 Aniketh Chavare (anikethchavare@zohomail.in)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# Imports
from colorama import init, Back, Fore, Style
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import PromptSession

# Initializing Colorama
init()

# Ignoring Keyboard Shortcuts
keyboard_bindings = KeyBindings()

@keyboard_bindings.add("c-c")
@keyboard_bindings.add("c-d")
@keyboard_bindings.add("c-z")
@keyboard_bindings.add("c-x")
def _(event):
    pass

# Function 1: Display Message
def display_message(
        message: str,
        color: str,
        background: str = None,
        bright: bool = False,
        dim: bool = False,
        prefix: str = "",
        suffix: str = ""
):
    """
    Displays a message.

    Args:
        message (String): The message to be displayed.
        color (String): The color of the message.
        background (String): The background color of the message.
        bright (Boolean): Whether the message needs to be bright.
        dim (Boolean): Whether the message needs to be dim.
        prefix (String): The custom prefix to be added to the message.
        suffix (String): The custom suffix to be added to the message.
    """

    # Color Variables
    background_colors = {
        "green": Back.GREEN,
        "red": Back.RED
    }

    colors = {
        "red": Fore.RED,
        "yellow": Fore.YELLOW,
        "black": Fore.BLACK,
        "green": Fore.GREEN,
        "white": Fore.WHITE
    }

    # Displaying the Message
    background = background_colors[background] if background is not None else ""
    bright = Style.BRIGHT if bright else ""
    dim = Style.DIM if dim else ""
    print(f"{prefix}{colors[color]}{background}{bright}{dim}{message}{Style.RESET_ALL}{suffix}")

# Function 2: Display Message Text
def display_message_text(
        username: str,
        short_client_id: str,
        message: str = "",
        type: str = "",
        only_text: bool = False
) -> str | None:
    """
    Displays incoming and outgoing messages.

    Args:
        username (String): The username to be displayed.
        short_client_id (String): The short client ID to be displayed.
        message (String): The message to be displayed.
        type (String): The type of message ('incoming' or 'outgoing').
        only_text (Boolean): Whether to return only the raw text.

    Returns: The message text if "only_text" is set to True.
    """

    # Displaying the Message Text
    prefix = "\r\033[K" if type == "incoming" else "\033[A\r\033[K"
    color = Fore.CYAN if type == "incoming" else Fore.GREEN

    if only_text:
        return f"{Fore.GREEN}[{username}@{short_client_id}]: {Fore.WHITE}{Style.RESET_ALL}"
    else:
        print(f"{prefix}{color}[{username}@{short_client_id}]: {Fore.WHITE}{message}{Style.RESET_ALL}")
        return None

# Function 3: Display Message Prompt
def display_message_prompt(username: str, short_client_id: str) -> None:
    """
    Displays a message prompt.

    Args:
        username (String): The username to be displayed.
        short_client_id (String): The short client ID to be displayed.
    """

    # Displaying the Message Prompt
    print(f"{Fore.GREEN}[{username}@{short_client_id}]: {Style.RESET_ALL}", end="", flush=True)

# Async Function 1: Display Prompt
async def display_prompt(message: str, color: str, prefix: str = ""):
    """
    Displays an 'input' prompt.

    Args:
        message (String): The message to be displayed.
        color (String): The color of the message.
        prefix (String): The custom prefix to be added to the message.

    Returns: An input prompt.
    """

    # Color Variable
    colors = {
        "red": Fore.RED,
        "yellow": Fore.YELLOW,
        "black": Fore.BLACK,
        "green": Fore.GREEN,
        "white": Fore.WHITE,
        "cyan": Fore.CYAN
    }

    session = PromptSession(key_bindings=keyboard_bindings)

    return (await session.prompt_async(ANSI(f"{prefix}{colors[color]}{message}{Fore.WHITE}"))).strip()