# ghost-protocol-client - modules/network.py

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
from modules import ui

import sys
import httpx

# Constants
SERVER_URL = "https://ghost-protocol.anikethchavare.com/generate-token"

# Async Function 1: Get Token Request
async def get_token_request(client_id: str, room_id: str, username: str, room_decision: str):
    """
    Sends an authentication request to the server for token generation.

    Args:
        client_id (String): The client ID of the member.
        room_id (String): The room ID of the member.
        username (String): The username of the member.
        room_decision (String): Whether to 'join' or `leave` the room.

    Returns (JSON): The token, along with extra information.
    """

    async with httpx.AsyncClient() as request_client:
        try:
            response = await request_client.post(
                SERVER_URL,
                json={
                    "client_id": client_id,
                    "room_id": room_id,
                    "username": username,
                    "action": room_decision
                }
            )

            if response.status_code == 404:
                ui.display_message(message="[!] ACCESS DENIED: Room ID does not exist.", color="red", prefix="\n")
                sys.exit(1)
            elif response.status_code == 409:
                ui.display_message(message="[!] ACCESS DENIED: Username taken by another member.", color="red", prefix="\n")
                sys.exit(1)

            response.raise_for_status()
            return response.json()
        except SystemExit:
            raise
        except Exception as e:
            ui.display_message(message=f"[!] TOKEN AUTHENTICATION ERROR: {e}", color="red", prefix="\n")
            raise e