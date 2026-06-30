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

import os
import sys
import uuid
import httpx
import base64
import random
import string
import asyncio
from colorama import init, Fore, Back, Style

from ably import AblyRealtime
from ably.types.presence import PresenceAction

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Constants
APP_VERSION = "v0.2.0"
SERVER_URL = "https://ghost-protocol.anikethchavare.com/generate-token"

# State & Encryption Keys
is_app_ready = False
last_event_was_presence = True

session_key = None
local_private_key = x25519.X25519PrivateKey.generate()
local_public_key = local_private_key.public_key()

# Initializing Colorama
init()

# Async Function 1: Presence Handler
async def presence_handler(channel, username: str, short_client_id: str):
    """ Listens for members entering or leaving the room-based channel. """

    # Nested Function 1: Presence Listener
    def presence_listener(member):
        global last_event_was_presence

        sender_id = member.client_id
        sender_username = member.data

        if sender_id == channel.ably.options.client_id:
            return

        prefix = "\r\033[K" if last_event_was_presence else "\r\033[K\n"

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

# Async Function 2: Receive Message Handler
async def receive_messages_handler(channel, username: str, short_client_id: str):
    """ Listens for incoming messages on the room-based channel. """

    # Nested Function 1: Listener
    def listener(message):
        global last_event_was_presence, session_key

        if message.name == "key_request" and session_key is not None:
            payload = message.data
            newcomer_id = payload.get("client_id")

            if newcomer_id != channel.ably.options.client_id:
                # Fetching Public Key from New Member
                peer_public_key = x25519.X25519PublicKey.from_public_bytes(base64.b64decode(payload.get("public_key")))
                shared_secret = local_private_key.exchange(peer_public_key)

                derived_wrapper_key = HKDF(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=None,
                    info=b"ghost-protocol-handshake"
                ).derive(shared_secret)

                wrapper_cipher = AESGCM(derived_wrapper_key)
                handshake_nonce = os.urandom(12)
                encrypted_session_key = wrapper_cipher.encrypt(handshake_nonce, session_key, None)

                our_public_encoded = base64.b64encode(local_public_key.public_bytes_raw()).decode("utf-8")

                # Sending Session Key to New Member
                asyncio.create_task(channel.publish(f"key_delivery:{newcomer_id}", {
                    "sender_public_key": our_public_encoded,
                    "nonce": base64.b64encode(handshake_nonce).decode('utf-8'),
                    "encrypted_session_key": base64.b64encode(encrypted_session_key).decode('utf-8')
                }))
        elif message.name == "message":
            payload = message.data
            sender_username = payload.get("username")
            sender_id = payload.get("client_id")

            if sender_username != username:
                if session_key is not None:
                    try:
                        # Decrypting the Message
                        raw_payload = base64.b64decode(payload.get("message").encode('utf-8'))
                        nonce = raw_payload[:12]
                        ciphertext = raw_payload[12:]

                        aes_gcm = AESGCM(session_key)
                        decrypted_message = aes_gcm.decrypt(nonce, ciphertext,None).decode('utf-8')

                        print(f"\r\033[K{Fore.CYAN}[{sender_username}@{sender_id.split('-')[4]}]: {Fore.WHITE}{decrypted_message}{Style.RESET_ALL}")
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
        peer_public_bytes = base64.b64decode(payload.get("sender_public_key"))
        nonce = base64.b64decode(payload.get("nonce"))
        encrypted_session_key = base64.b64decode(payload.get("encrypted_session_key"))

        sender_public_key = x25519.X25519PublicKey.from_public_bytes(peer_public_bytes)
        shared_secret = local_private_key.exchange(sender_public_key)

        derived_wrapper_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"ghost-protocol-handshake",
        ).derive(shared_secret)

        wrapper_cipher = AESGCM(derived_wrapper_key)
        session_key = wrapper_cipher.decrypt(nonce, encrypted_session_key, None)

        print(f"\r\033[K{Fore.YELLOW}[*] Cryptographic Handshake: Session key securely established.{Style.RESET_ALL}")
        if is_app_ready:
            print(f"{Fore.GREEN}[{username}@{short_client_id}]: {Style.RESET_ALL}", end="", flush=True)

    await channel.subscribe(f"key_delivery:{channel.ably.options.client_id}", delivery_listener)

# Async Function 3: Send Message Handler
async def send_messages_handler(channel, username: str, short_client_id: str):
    """ Handles user terminal input and publishes messages in the room-based channel. """

    global last_event_was_presence
    loop = asyncio.get_event_loop()

    while True:
        try:
            prompt = f"{Fore.GREEN}[{username}@{short_client_id}]: {Fore.WHITE}{Style.RESET_ALL}"
            message_text = await loop.run_in_executor(None, input, prompt)
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
                # Encrypting the Message using AES-256 (GCM)
                aes_gcm = AESGCM(session_key)
                nonce = os.urandom(12)
                ciphertext = aes_gcm.encrypt(nonce, message_text.encode("utf-8"),None)
                encoded_payload = base64.b64encode(nonce + ciphertext).decode("utf-8")
            else:
                print(f"{Fore.RED}[!] TRANSMISSION FAILURE: Cryptographic handshake is not established.{Style.RESET_ALL}")
                continue

            payload = {
                "client_id": channel.ably.options.client_id,
                "username": username,
                "message": encoded_payload
            }

            await channel.publish("message", payload)
        except Exception as e:
            print(f"\n{Fore.RED}[!] TRANSMISSION FAILURE: {e}")

# Async Function 4: Main
async def main():
    global session_key
    room_id = None

    # Set the Custom Terminal Title
    utils.set_terminal_title()

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

        session_key = AESGCM.generate_key(bit_length=256)
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
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(SERVER_URL, json={"client_id": client_id, "room_id": room_id})

                if response.status_code != 200:
                    raise Exception(f"ServerError: Server rejected hand-shake: {response.status_code}")

                return response.json()
            except Exception as e:
                print(f"\n{Fore.RED}[!] TOKEN AUTHENTICATION ERROR: {e}{Style.RESET_ALL}")
                raise e

    # Initializing Ably via AblyRealtime
    async with AblyRealtime(auth_callback=get_token_request, client_id=client_id) as client:
        await client.connection.once_async("connected")

        # Mapping Channel Name to the Capability Filter
        channel_name = f"room:{room_id}"
        channel = client.channels.get(channel_name)

        # Establish Concurrent Streaming Tasks for Sending & Receiving Data
        presence_task = None
        receive_task = None
        send_task = None

        try:
            await channel.attach()

            # Setting the Presence Handler
            presence_task = asyncio.create_task(presence_handler(channel, username, client_id.split("-")[4]))
            await asyncio.sleep(0.1)

            # Fetching the Roster of Current Members
            presence_members = await channel.presence.get()

            # Checking if Room Exists
            if room_decision == "join":
                if not presence_members:
                    print(f"\n{Fore.RED}[!] ACCESS DENIED: Room ID does not exist.{Style.RESET_ALL}")
                    return

            # Checkin if Username is Taken
            if any(member.data == username for member in presence_members):
                print(f"\n{Fore.RED}[!] ACCESS DENIED: Username taken by another member.{Style.RESET_ALL}")
                return

            # Setting the Receive Messages Handler
            receive_task = asyncio.create_task(receive_messages_handler(channel, username, client_id.split("-")[4]))

            await asyncio.sleep(0.2)
            await channel.presence.enter_client(client_id, username)

            # Initializing the Cryptographic Handshake
            if room_decision == "join":
                await channel.publish("key_request",{
                    "client_id": client_id,
                    "public_key": base64.b64encode(local_public_key.public_bytes_raw()).decode("utf-8")
                })

            # Displaying Connection Messages
            print(f"\n{Fore.BLACK}{Back.GREEN}[+] CONNECTION ESTABLISHED SECURELY // ENCRYPTION ACTIVE{Style.RESET_ALL}")
            print(f"{Style.DIM}Type your message or execute '/exit' to terminate connection.{Style.RESET_ALL}")
            print()

            # Signaling the App is Ready
            global is_app_ready
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