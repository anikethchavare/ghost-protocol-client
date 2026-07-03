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
import os
import sys

# Function 1: Set Terminal Title
def set_terminal_title(app_version: str) -> None:
    """
    Sets the title of the terminal window.

    Args:
        app_version (String): The version of the app in SemVer.
    """

    if sys.platform.startswith("win"):
        os.system(f"title Ghost Protocol {app_version}")
    else:
        print(f"\033]0;Ghost Protocol {app_version}\a", end="", flush=True)