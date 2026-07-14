# ghost-protocol-client - modules/utils.py

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
from modules import ui, encryption

import os
import sys
import uuid
import string
import random
import pywinctl

# Constants
APP_VERSION = "v1.0.0"

# Function 1: Set Terminal Title
def set_terminal_title():
    """ Sets the title of the terminal window. """

    if sys.platform.startswith("win"):
        os.system(f"title Ghost Protocol {APP_VERSION}")
    else:
        print(f"\033]0;Ghost Protocol {APP_VERSION}\a", end="", flush=True)

# Function 2: Maximize Terminal
def maximize_terminal():
    """ Expands the terminal window size to the maximum. """

    active_window = pywinctl.getActiveWindow()

    if active_window:
        active_window.maximize()

# Function 3: Initiate Onboarding
def initiate_onboarding(session_key_ready):
    """
    Initiates the onboarding process for the member.

    Args:
        session_key_ready (asyncio.Event()): Asynchronous signaling flag whether the session key is ready.

    Returns: A tuple containing client information or "None" if an error occurs.
    """

    # Variables
    session_key = None
    room_id = None

    # Displaying Initial Messages
    ui.display_message(message="=== GHOST PROTOCOL (SECURE COMMS TERMINAL) ===", color="green", bright=True)
    ui.display_message(message=f"Status: CLEAR // Protocol: Ghost-E2EE // Version: {APP_VERSION}", color="white", dim=True)

    # Prompting User for Username & Room ID
    username = ui.display_prompt(message="USERNAME: ", color="cyan", prefix="\n")

    if not username:
        ui.display_message(message="[!] ACCESS DENIED: Username cannot be empty.", color="red", prefix="\n")
        return None

    room_decision = ui.display_prompt(message="CREATE OR JOIN ROOM: ", color="cyan").lower()

    if not room_decision or room_decision not in ["create", "join"]:
        ui.display_message(message="[!] ACCESS DENIED: Enter a valid input ('create' or 'join').", color="red", prefix="\n")
        return None

    if room_decision == "create":
        room_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))

        session_key = encryption.generate_key(length=256)
        session_key_ready.set()
    elif room_decision == "join":
        room_id = ui.display_prompt(message="ROOM ID: ", color="cyan")

    if not room_id or len(room_id) != 8:
        ui.display_message(message="[!] ACCESS DENIED: Room ID is required and must be exactly 8 characters.", color="red")
        return None

    # Generating the Client ID (UUID v4)
    client_id = str(uuid.uuid4())

    return username.replace(" ", "-"), room_decision, room_id, session_key, client_id