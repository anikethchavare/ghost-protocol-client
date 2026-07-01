# ghost-protocol-client - app.py

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
from modules import utils
from modules import encryption

import os
import sys
import uuid
import time
import httpx
import orjson
import random
import string
import asyncio
from base64 import b64encode, b64decode
from colorama import init, Fore, Back, Style

from ably import AblyRealtime
from ably.types.presence import PresenceAction

# Constants
APP_VERSION = "v0.2.0"
MAX_REPLAY_WINDOW = 5.0
SERVER_URL = "https://ghost-protocol.anikethchavare.com/generate-token"

# State & Encryption Keys
is_app_ready = False
last_event_was_presence = True

session_key = None
local_public_key, local_private_key = encryption.generate_key_pair()

# Initializing Colorama
init()

# Async Function 1: Presence Handler
async def presence_handler(channel, username: str, short_client_id: str):
    """
    Listens for members entering or leaving the room-based channel.

    Args:
        channel: The channel to listen for.
        username (String): The username of the member.
        short_client_id (String): The last part of the client's ID (UUID v4).
    """

    # Nested Function 1: Presence Listener
    def presence_listener(member):
        global last_event_was_presence
        sender_id = member.client_id
        sender_username = member.data

        if sender_id == channel.ably.options.client_id:
            return

        prefix = "\r\033[K" if last_event_was_presence else "\r\033[K\n"

        # Displays Message According to Action
        if member.action == PresenceAction.ENTER:
            print(f"{prefix}{Fore.YELLOW}[*] MEMBER JOINED: {sender_username}@{sender_id.split('-')[4]} has entered the room.{Style.RESET_ALL}\n")
            if is_app_ready:
                print(f"{Fore.GREEN}[{username}@{short_client_id}]: {Style.RESET_ALL}", end="", flush=True)
        elif member.action in [PresenceAction.LEAVE, PresenceAction.ABSENT]:
            print(f"{prefix}{Fore.RED}[*] MEMBER LEFT: {sender_username}@{sender_id.split('-')[4]} has left the room.{Style.RESET_ALL}\n")
            if is_app_ready:
                print(f"{Fore.GREEN}[{username}@{short_client_id}]: {Style.RESET_ALL}", end="", flush=True)

        last_event_was_presence = True

    await channel.presence.subscribe(presence_listener)

# Async Function 2: Receive Messages Handler
async def receive_messages_handler(channel, username: str, short_client_id: str):
    """
    Listens for incoming messages on the room-based channel.

    Args:
        channel: The channel to listen for.
        username (String): The username of the member.
        short_client_id (String): The last part of the client's ID (UUID v4).
    """

    # Nested Function 1: Listener
    def listener(message):
        global last_event_was_presence, session_key

        if message.name == "key_request" and session_key is not None:
            payload = message.data
            new_member_client_id = payload.get("client_id")

            if new_member_client_id != channel.ably.options.client_id:

                # Nested Async Function 1: Process Key Delivery
                async def process_key_delivery():
                    presence_members = await channel.presence.get()
                    active_client_ids = [member.client_id for member in presence_members if member.client_id != new_member_client_id]

                    if not active_client_ids:
                        return

                    active_client_ids.sort()
                    elected_host_id = active_client_ids[0]

                    if channel.ably.options.client_id == elected_host_id:
                        # Encrypting Session Key & Sending it to New Member
                        handshake_nonce = os.urandom(12)
                        encrypted_session_key = encryption.encrypt_message(
                            key=encryption.generate_wrapper_key(shared_secret=local_private_key.exchange(encryption.derive_public_key(b64decode(payload.get("public_key"))))),
                            nonce=handshake_nonce,
                            data=session_key
                        )

                        # Channel Publish (key_delivery): Sending Session Key to New Member
                        await channel.publish(f"key_delivery:{new_member_client_id}", {
                            "sender_public_key": b64encode(local_public_key.public_bytes_raw()).decode("utf-8"),
                            "nonce": b64encode(handshake_nonce).decode('utf-8'),
                            "encrypted_session_key": b64encode(encrypted_session_key).decode('utf-8')
                        })

                # Executing the Key Delivery Process Asynchronously
                asyncio.create_task(process_key_delivery())
        elif message.name == "message":
            payload = message.data

            if session_key is not None:
                try:
                    # Decrypting Payload & Extracting Information
                    raw_payload = b64decode(payload.get("encrypted_payload").encode("utf-8"))
                    decrypted_payload = orjson.loads(encryption.decrypt_message(key=session_key, nonce=raw_payload[:12], data=raw_payload[12:]))

                    sender_username = decrypted_payload.get("username")
                    decrypted_message = decrypted_payload.get("message")
                    timestamp_str = decrypted_payload.get("timestamp")

                    if sender_username == username:
                        return

                    if not timestamp_str or not decrypted_message:
                        print(f"\r\033[K{Fore.RED}[!] SECURITY ALERT: Received malformed message payload.{Style.RESET_ALL}")
                        return

                    if abs(time.time() - float(timestamp_str)) > MAX_REPLAY_WINDOW:
                        print(f"\r\033[K{Fore.RED}[!] SECURITY ALERT: Rejected message from {sender_username} due to replay.{Style.RESET_ALL}")
                        if is_app_ready:
                            print(f"{Fore.GREEN}[{username}@{short_client_id}]: {Fore.WHITE}{Style.RESET_ALL}", end="", flush=True)
                        return

                    print(f"\r\033[K{Fore.CYAN}[{sender_username}@{decrypted_payload.get("client_id").split('-')[4]}]: {Fore.WHITE}{decrypted_message}{Style.RESET_ALL}")
                    if is_app_ready:
                        print(f"{Fore.GREEN}[{username}@{short_client_id}]: {Fore.WHITE}{Style.RESET_ALL}", end="", flush=True)

                    last_event_was_presence = False
                except Exception:
                    print(f"\r\033[K{Fore.RED}[!] ENCRYPTION FAILURE: Failed to decrypt incoming payload.{Style.RESET_ALL}")
            else:
                print(f"\r\033[K{Fore.YELLOW}[*] Cryptographic Handshake: Awaiting session key verification...{Style.RESET_ALL}")

    await channel.subscribe(listener)

    # Nested Function 2: Delivery Listener (Derives Session Key)
    def delivery_listener(message):
        global session_key

        if session_key is not None:
            return

        payload = message.data
        session_key = encryption.decrypt_message(
            key=encryption.generate_wrapper_key(shared_secret=local_private_key.exchange(encryption.derive_public_key(b64decode(payload.get("sender_public_key"))))),
            nonce=b64decode(payload.get("nonce")),
            data=b64decode(payload.get("encrypted_session_key"))
        )

        print(f"\r\033[K{Fore.YELLOW}[*] Cryptographic Handshake: Session key securely established.{Style.RESET_ALL}")
        if is_app_ready:
            print(f"{Fore.GREEN}[{username}@{short_client_id}]: {Style.RESET_ALL}", end="", flush=True)

    await channel.subscribe(f"key_delivery:{channel.ably.options.client_id}", delivery_listener)

# Async Function 3: Send Messages Handler
async def send_messages_handler(channel, username: str, short_client_id: str):
    """
    Handles user terminal input and publishes messages in the room-based channel.

    Args:
        channel: The channel to listen for.
        username (String): The username of the member.
        short_client_id (String): The last part of the client's ID (UUID v4).
    """

    global last_event_was_presence
    loop = asyncio.get_event_loop()

    while True:
        try:
            message_text = await loop.run_in_executor(None, input,f"{Fore.GREEN}[{username}@{short_client_id}]: {Fore.WHITE}{Style.RESET_ALL}")
        except (asyncio.CancelledError, KeyboardInterrupt):
            break

        message_text = message_text.strip()

        if not message_text:
            continue

        if message_text.lower() == "/exit":
            break

        try:
            print(f"\033[A\r\033[K{Fore.GREEN}[{username}@{short_client_id}]: {Fore.WHITE}{message_text}{Style.RESET_ALL}")
            last_event_was_presence = False

            if session_key is not None:
                # Assembling the Payload
                payload = orjson.dumps({
                    "timestamp": str(time.time()),
                    "client_id": channel.ably.options.client_id,
                    "username": username,
                    "message": message_text
                })

                # Encrypting the Data
                nonce = os.urandom(12)
                encrypted_payload = b64encode(nonce + encryption.encrypt_message(key=session_key, nonce=nonce, data=payload)).decode("utf-8")
            else:
                print(f"{Fore.RED}[!] TRANSMISSION FAILURE: Cryptographic handshake is not established.{Style.RESET_ALL}")
                continue

            # Channel Publish (message): Sending Encrypted Payload
            await channel.publish("message", {
                "encrypted_payload": encrypted_payload
            })
        except Exception as e:
            print(f"\n{Fore.RED}[!] TRANSMISSION FAILURE: {e}")

# Async Function 4: Main
async def main():
    global session_key, is_app_ready
    room_id = None

    # Set the Custom Terminal Title
    utils.set_terminal_title(APP_VERSION)

    # Displaying Initial Messages
    print(f"{Fore.GREEN}{Style.BRIGHT}=== GHOST PROTOCOL (SECURE COMMS TERMINAL) ==={Style.RESET_ALL}")
    print(f"{Style.DIM}Status: CLEAR // Protocol: Ghost-E2EE // Version: {APP_VERSION}{Style.RESET_ALL}")
    print(f"{Fore.RED}[!] WARNING: Do not use for production or highly sensitive data.{Style.RESET_ALL}")

    # Prompting User for Username & Room ID
    username = input(f"\n{Fore.CYAN}USERNAME: {Fore.WHITE}").strip(); print(Style.RESET_ALL, end="")

    if not username:
        print(f"\n{Fore.RED}[!] ACCESS DENIED: Username cannot be empty.{Style.RESET_ALL}")
        return

    room_decision = input(f"{Fore.CYAN}CREATE OR JOIN ROOM: {Fore.WHITE}").strip().lower(); print(Style.RESET_ALL, end="")

    if not room_decision or room_decision not in ["create", "join"]:
        print(f"\n{Fore.RED}[!] ACCESS DENIED: Enter a valid input ('create' or 'join').{Style.RESET_ALL}")
        return

    if room_decision == "create":
        room_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
        print(f"\n{Style.DIM}ROOM ID: {room_id}{Style.RESET_ALL}")

        session_key = encryption.generate_key(length=256)
    elif room_decision == "join":
        room_id = input(f"{Fore.CYAN}ROOM ID: {Fore.WHITE}").strip(); print(Style.RESET_ALL, end="")
        print()

    if not room_id or len(room_id) != 8:
        print(f"{Fore.RED}[!] ACCESS DENIED: Room ID is required and must be exactly 8 characters.{Style.RESET_ALL}")
        return

    # Generating the Client ID (UUID v4)
    username = username.replace(" ", "-")
    client_id = str(uuid.uuid4())

    print(f"{Style.DIM}SHORT CLIENT ID: {client_id.split('-')[4]}{Style.RESET_ALL}")
    print(f"{Style.DIM}CLIENT ID: {client_id}{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}[*] Requesting authentication token and establishing connection...{Style.RESET_ALL}")

    # Nested Async Function 1: Get Token Request
    async def get_token_request(*args, **kwargs):
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
                    print(f"\n{Fore.RED}[!] ACCESS DENIED: Room ID does not exist.{Style.RESET_ALL}")
                    sys.exit(1)
                elif response.status_code == 409:
                    print(f"\n{Fore.RED}[!] ACCESS DENIED: Username taken by another member.{Style.RESET_ALL}")
                    sys.exit(1)

                response.raise_for_status()
                return response.json()
            except SystemExit:
                raise
            except Exception as e:
                print(f"\n{Fore.RED}[!] TOKEN AUTHENTICATION ERROR: {e}{Style.RESET_ALL}")
                raise e

    # Initializing Ably via AblyRealtime
    async with AblyRealtime(auth_callback=get_token_request, client_id=client_id) as client:
        await client.connection.once_async("connected")

        # Mapping Channel Name to the Capability Filter
        channel = client.channels.get(f"room:{room_id}")

        # Establish Concurrent Streaming Tasks for Sending & Receiving Data
        presence_task = None
        receive_task = None
        send_task = None

        try:
            await channel.attach()

            # Setting the Presence Handler
            presence_task = asyncio.create_task(presence_handler(channel, username, client_id.split("-")[4]))
            await asyncio.sleep(0.1)

            # Setting the Receive Messages Handler
            receive_task = asyncio.create_task(receive_messages_handler(channel, username, client_id.split("-")[4]))

            await asyncio.sleep(0.2)
            await channel.presence.enter_client(client_id, username)

            # Initializing the Cryptographic Handshake
            if room_decision == "join":
                # Channel Publish (key_request): Requesting Members for Session Key
                await channel.publish("key_request", {
                    "client_id": client_id,
                    "public_key": b64encode(local_public_key.public_bytes_raw()).decode("utf-8")
                })

            # Displaying Connection Messages
            print(f"\n{Fore.BLACK}{Back.GREEN}[+] CONNECTION ESTABLISHED SECURELY // ENCRYPTION ACTIVE{Style.RESET_ALL}")
            print(f"{Style.DIM}Type your message or execute '/exit' to terminate connection.{Style.RESET_ALL}")
            print()

            # Signaling the App is Ready
            is_app_ready = True

            # Setting the Send Messages Handler
            send_task = asyncio.create_task(send_messages_handler(channel, username, client_id.split("-")[4]))
            await send_task
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}[!] SIGNAL INTERRUPTED BY USER{Style.RESET_ALL}")
        finally:
            if presence_task:
                presence_task.cancel()

                try:
                    await presence_task
                except asyncio.CancelledError:
                    pass

            if receive_task:
                receive_task.cancel()

                try:
                    await receive_task
                except asyncio.CancelledError:
                    pass

            if send_task:
                try:
                    await channel.presence.leave_client(client_id)
                except Exception:
                    pass

                # Displaying Connection Termination Messages
                print(f"\n\n\n\033[A\r\033[K{Fore.YELLOW}[*] Terminating active session in room {room_id}...{Style.RESET_ALL}")
                print(f"\n{Fore.BLACK}{Back.RED}[!] SECURE CONNECTION TERMINATED{Style.RESET_ALL}")

# Running the Application
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (Exception, KeyboardInterrupt, asyncio.CancelledError):
        print(f"\n\n{Fore.RED}[!] EXECUTION ABORTED{Style.RESET_ALL}")
    finally:
        input(f"\nProcess finished. Press ENTER to close the terminal.{Style.RESET_ALL}")
        sys.exit(0)