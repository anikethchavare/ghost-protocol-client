# ghost-protocol-client - modules/encryption.py

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
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Function 1: Generate Wrapper Key
def generate_wrapper_key(shared_secret):
    """
    Generates the wrapper key from the given public-private key pair.

    Args:
        shared_secret: The set of public and private keys.

    Returns: The wrapper key.
    """

    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"ghost-protocol-handshake"
    ).derive(shared_secret)

# Function 2: Generate Key
def generate_key(length: int):
    """
    Generates an AES-GCM key.

    Args:
        length (Integer): The length of the key.

    Returns: The AES-GCM key of the given length.
    """

    return AESGCM.generate_key(bit_length=length)

# Function 3: Generate Key Pair
def generate_key_pair():
    """
    Generates a X25519 key pair.

    Returns: The public-private key pair.
    """

    private_key = x25519.X25519PrivateKey.generate()
    public_key = private_key.public_key()

    return public_key, private_key

# Function 4: Encrypt Message
def encrypt_message(key, nonce, data):
    """
    Encrypts the data using the AES key.

    Args:
        key: The AES-GCM key.
        nonce: The nonce of the AES-GCM key.
        data: The data to be encrypted.

    Returns: The encrypted data.
    """

    return AESGCM(key).encrypt(nonce, data, None)

# Function 5: Decrypt Message
def decrypt_message(key, nonce, data):
    """
    Decrypts the ciphertext using the AES key.

    Args:
        key: The AES-GCM key.
        nonce: The nonce of the AES-GCM key.
        data: The data to be decrypted.

    Returns: The decrypted data.
    """

    return AESGCM(key).decrypt(nonce, data, None)

# Function 6: Derive Public Key
def derive_public_key(public_key_bytes: bytes):
    """
    Derives the X25519 public key from the given bytes.

    Args:
        public_key_bytes (Bytes): The bytes of the X25519 public key.

    Returns: The public key in X25519 format.
    """

    return x25519.X25519PublicKey.from_public_bytes(public_key_bytes)