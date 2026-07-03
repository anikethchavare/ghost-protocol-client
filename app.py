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
from modules import ui, utils, network, encryption

import os
import sys
import uuid
import time
import orjson
import random
import string
import asyncio
from base64 import b64encode, b64decode

from ably import AblyRealtime
from ably.types.presence import PresenceAction

# Constants
APP_VERSION = "v1.0.0"
MAX_REPLAY_WINDOW = 5.0

# State & Encryption Keys
is_app_ready = False
last_event_was_presence = True

session_key = None
session_key_ready = asyncio.Event()
local_public_key, local_private_key = encryption.generate_key_pair()

# Async Function 1: Presence Handler
async def presence_handler(channel, username: str, short_client_id: str):
    """
    Listens for members entering or leaving the room-based channel.

    Args:
        channel: The channel to listen for.
        username (String): The username of the member.
        short_client_id (String): The last part of the client's ID (UUID v4).
    """

    # Nested Async Function 1: Presence Listener
    async def presence_listener(member):
        global last_event_was_presence, session_key
        sender_id = member.client_id

        sender_data = member.data
        sender_username = sender_data.get("username") if isinstance(sender_data, dict) else sender_data

        # Nested-2 Async Function 1: Process Key Rotation
        async def process_key_rotation():
            global session_key, is_app_ready

            presence_payload = await channel.presence.get()
            presence_members = getattr(presence_payload, 'items', presence_payload)
            active_client_ids = sorted([m.client_id for m in presence_members])

            if not active_client_ids:
                return False

            # Setting a Host
            elected_host_id = active_client_ids[0]

            if channel.ably.options.client_id == elected_host_id:
                # Generating a New Session Key
                session_key = encryption.generate_key(length=256)
                session_key_ready.set()

                if not is_app_ready:
                    ui.display_message(message="[*] Cryptographic Handshake: Session key securely established.", color="yellow", prefix="\r\033[K")

                for active_member in presence_members:
                    if active_member.client_id == channel.ably.options.client_id:
                        continue

                    active_member_data = active_member.data

                    if not isinstance(active_member_data, dict) or "public_key" not in active_member_data:
                        continue

                    # Encrypting the New Session Key
                    handshake_nonce = os.urandom(12)
                    encrypted_new_key = encryption.encrypt_message(
                        key=encryption.generate_wrapper_key(shared_secret=local_private_key.exchange(encryption.derive_public_key(public_key_bytes=b64decode(active_member_data.get("public_key"))))),
                        nonce=handshake_nonce,
                        data=session_key
                    )

                    # Channel Publish (key_delivery): Sending New Session Key to Each Member
                    await channel.publish(f"key_delivery:{active_member.client_id}", {
                        "sender_public_key": b64encode(local_public_key.public_bytes_raw()).decode("utf-8"),
                        "nonce": b64encode(handshake_nonce).decode('utf-8'),
                        "encrypted_session_key": b64encode(encrypted_new_key).decode('utf-8')
                    })

                return True

            return False

        await process_key_rotation()

        if sender_id == channel.ably.options.client_id:
            return

        prefix = "\r\033[K" if last_event_was_presence else "\r\033[K\n"

        # Displays Message According to Action
        if member.action == PresenceAction.ENTER:
            ui.display_message(message=f"[*] MEMBER JOINED: {sender_username}@{sender_id.split('-')[4]} has entered the room.", color="yellow", prefix=prefix, suffix="\n")
            if is_app_ready:
                ui.display_message_prompt(username=username, short_client_id=short_client_id)
        elif member.action in [PresenceAction.LEAVE, PresenceAction.ABSENT]:
            ui.display_message(message=f"[*] MEMBER LEFT: {sender_username}@{sender_id.split('-')[4]} has left the room.", color="red", prefix=prefix, suffix="\n")
            if is_app_ready:
                ui.display_message_prompt(username=username, short_client_id=short_client_id)

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

        if message.name == "message":
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
                        ui.display_message(message="[!] SECURITY ALERT: Received malformed message payload.", color="red", prefix="\r\033[K")
                        return

                    if abs(time.time() - float(timestamp_str)) > MAX_REPLAY_WINDOW:
                        ui.display_message(message=f"[!] SECURITY ALERT: Rejected message from {sender_username} due to replay.", color="red", prefix="\r\033[K")
                        if is_app_ready:
                            ui.display_message_prompt(username=username, short_client_id=short_client_id)
                        return

                    ui.display_message_text(username=username, short_client_id=decrypted_payload.get("client_id").split('-')[4], message=decrypted_message, type="incoming")
                    if is_app_ready:
                        ui.display_message_prompt(username=username, short_client_id=short_client_id)

                    last_event_was_presence = False
                except Exception:
                    ui.display_message(message="[!] ENCRYPTION FAILURE: Failed to decrypt incoming payload.", color="red", prefix="\r\033[K")
            else:
                ui.display_message(message="[*] Cryptographic Handshake: Awaiting session key verification...", color="yellow", prefix="\r\033[K")

    await channel.subscribe(listener)

    # Nested Function 2: Delivery Listener (Derives Session Key)
    def delivery_listener(message):
        global session_key, session_key_ready

        # Decrypting the Session Key
        payload = message.data
        session_key = encryption.decrypt_message(
            key=encryption.generate_wrapper_key(shared_secret=local_private_key.exchange(encryption.derive_public_key(b64decode(payload.get("sender_public_key"))))),
            nonce=b64decode(payload.get("nonce")),
            data=b64decode(payload.get("encrypted_session_key"))
        )

        session_key_ready.set()

        if not is_app_ready:
            ui.display_message(message="[*] Cryptographic Handshake: Session key securely established.", color="yellow", prefix="\r\033[K")

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
    loop = asyncio.get_running_loop()

    while True:
        try:
            message_text = await loop.run_in_executor(None, input,ui.display_message_text(username=username, short_client_id=short_client_id, only_text=True))
        except (asyncio.CancelledError, KeyboardInterrupt):
            break

        message_text = message_text.strip()

        if not message_text:
            continue

        if message_text.lower() == "/exit":
            break

        try:
            ui.display_message_text(username=username, short_client_id=short_client_id, message=message_text, type="outgoing")
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
                ui.display_message(message="[!] TRANSMISSION FAILURE: Cryptographic handshake is not established.", color="red")
                continue

            # Channel Publish (message): Sending Encrypted Payload
            await channel.publish("message", {
                "encrypted_payload": encrypted_payload
            })
        except Exception as e:
            ui.display_message(message=f"[!] TRANSMISSION FAILURE: {e}", color="red", prefix="\n")

# Async Function 4: Main
async def main():
    """ The main function to be executed. """

    global session_key, is_app_ready
    room_id = None

    # Set the Custom Terminal Title
    utils.set_terminal_title(APP_VERSION)

    # Displaying Initial Messages
    ui.display_message(message="=== GHOST PROTOCOL (SECURE COMMS TERMINAL) ===", color="green", bright=True)
    ui.display_message(message=f"Status: CLEAR // Protocol: Ghost-E2EE // Version: {APP_VERSION}", color="white", dim=True)
    ui.display_message(message="[!] WARNING: Provided 'as is' without warranty. Use at your own risk.", color="red")

    # Prompting User for Username & Room ID
    username = ui.display_prompt(message="USERNAME: ", color="cyan", prefix="\n")

    if not username:
        ui.display_message(message="[!] ACCESS DENIED: Username cannot be empty.", color="red", prefix="\n")
        return

    room_decision = ui.display_prompt(message="CREATE OR JOIN ROOM: ", color="cyan").lower()

    if not room_decision or room_decision not in ["create", "join"]:
        ui.display_message(message="[!] ACCESS DENIED: Enter a valid input ('create' or 'join').", color="red", prefix="\n")
        return

    if room_decision == "create":
        room_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
        ui.display_message(message=f"ROOM ID: {room_id}", color="white", dim=True, prefix="\n")

        session_key = encryption.generate_key(length=256)
        session_key_ready.set()
    elif room_decision == "join":
        room_id = ui.display_prompt(message="ROOM ID: ", color="cyan")
        print()

    if not room_id or len(room_id) != 8:
        ui.display_message(message="[!] ACCESS DENIED: Room ID is required and must be exactly 8 characters.", color="red")
        return

    # Generating the Client ID (UUID v4)
    username = username.replace(" ", "-")
    client_id = str(uuid.uuid4())

    ui.display_message(message=f"SHORT CLIENT ID: {client_id.split('-')[4]}", color="white", dim=True)
    ui.display_message(message=f"CLIENT ID: {client_id}", color="white", dim=True)
    ui.display_message(message="[*] Requesting authentication token and establishing connection...", color="yellow", prefix="\n")

    # Initializing Ably via AblyRealtime
    async with AblyRealtime(
        auth_callback=lambda _: network.get_token_request(client_id=client_id, room_id=room_id, username=username, room_decision=room_decision),
        client_id=client_id
    ) as client:
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

            # Sharing Presence Data When Joining a Room
            await channel.presence.enter_client(client_id, {
                "username": username,
                "public_key": b64encode(local_public_key.public_bytes_raw()).decode("utf-8")
            })

            # Displaying Connection Messages
            if room_decision == "join":
                await session_key_ready.wait()
            else:
                await asyncio.sleep(0.1)

            ui.display_message(message="[+] CONNECTION ESTABLISHED SECURELY // ENCRYPTION ACTIVE", color="black", background="green", prefix="\n")
            ui.display_message(message="Type your message or execute '/exit' to terminate connection.", color="white", dim=True)
            print()

            # Signaling the App is Ready
            is_app_ready = True

            # Setting the Send Messages Handler
            send_task = asyncio.create_task(send_messages_handler(channel, username, client_id.split("-")[4]))
            await asyncio.gather(presence_task, receive_task, send_task)
        except KeyboardInterrupt:
            ui.display_message(message="[!] SIGNAL INTERRUPTED BY USER", color="red", prefix="\n")
        finally:
            for task in [presence_task, receive_task, send_task]:
                if task:
                    if task in [presence_task, receive_task]:
                        task.cancel()

                    try:
                        if send_task:
                            await channel.presence.leave_client(client_id)
                        else:
                            await task
                    except (Exception, asyncio.CancelledError):
                        pass

            # Displaying Connection Termination Messages
            ui.display_message(message=f"[*] Terminating active session in room {room_id}...", color="yellow", prefix="\n\n\n\033[A\r\033[K")
            ui.display_message(message="[!] SECURE CONNECTION TERMINATED", color="black", background="red", prefix="\n")

# Running the Application
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    except Exception as e:
        ui.display_message(message=f"[!] EXECUTION ABORTED: {e}", color="red", prefix="\n\n")
    finally:
        input(f"\nProcess finished. Press ENTER to close the terminal.")
        sys.exit(0)