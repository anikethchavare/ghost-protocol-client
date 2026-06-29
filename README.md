<div align="center"><h1>anikethchavare // Ghost Protocol (Client)</h1></div>
<div align="center"><strong>This is the client application of Ghost Protocol, an end-to-end encrypted (E2EE) terminal chat application built <br> with Python and WebSockets, routing communications securely without leaving a trace.</strong></div>

<br>

<div align="center"><img width="750" alt="Main Image for README (Terminal)" src="https://github.com/user-attachments/assets/9baf2979-f190-4dc2-a643-a43a3466d446"></div>

<br>

<div align="center">
    ⚠️ <a href="https://github.com/anikethchavare/ghost-protocol-client/issues">Report an Issue</a>
</div>

<br>

<div align="center">
    <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" alt="Python">&nbsp;&nbsp;
    <img src="https://img.shields.io/badge/Ably-F9A826?style=for-the-badge&logo=ably&logoColor=white" alt="Ably">&nbsp;&nbsp;
    <img src="https://img.shields.io/badge/Cryptography-000000?style=for-the-badge&logo=gitpod&logoColor=white" alt="Cryptography">&nbsp;&nbsp;
    <img src="https://img.shields.io/badge/Terminal-4EAA25?style=for-the-badge&logo=gnumetallink&logoColor=white" alt="Terminal">
    <br><br>
    <img src="https://img.shields.io/badge/version-0.1.0-blue?style=for-the-badge&logo=github&logoColor=white" alt="Version">&nbsp;&nbsp;
    <img src="https://img.shields.io/badge/license-Apache_2.0-blue?style=for-the-badge&logo=apache&logoColor=white" alt="Apache 2.0 License">&nbsp;&nbsp;
    <img src="https://img.shields.io/badge/maintained-yes-brightgreen?style=for-the-badge&logo=checkmarx&logoColor=white" alt="Maintenance: Active">
</div>

<hr>

## 1. ⚠️ Important Status: Unstable Release (v0.1.0)

This release is a highly functional demonstration of asynchronous E2EE communication over a real-time pub/sub network. It is **not** currently audited or hardened for production environments.

### Known Limitations (Fixes slated for v1.0.0):
- **No Forward Secrecy:** Room session keys are static per session lifecycle and do not rotate when members leave or join.
- **Deterministic Identities:** User IDs are generated via UUIDv5 on the client side, which lacks a central server-side authority validation.
- **Replay Attacks:** Message payloads currently lack temporal validations like sequence numbers or expiration timestamps.
- **Handshake Race Conditions:** Multiple active peers will simultaneously attempt to fulfill a newcomer's session key request.

*Do not use this version to transmit highly sensitive information or real production secrets.*

<hr>

## 2. 🛠️ Features & Tech Stack

This lightweight CLI script serves as the interactive frontend interface for the **Ghost Protocol** room-based chat application.

1. **End-to-End Encryption:** Uses modern, industry-standard cryptographic primitives featuring `X25519` for peer-to-peer key handshakes, `HKDF` for ephemeral key derivation, and `AES-256-GCM` for authenticated data packet encryption.
2. **Real-Time Mesh Pub/Sub:** Driven by the [Ably Python SDK](https://github.com/ably/ably-python) to handle multiplexed, low-latency room communication streams concurrently.
3. **Asynchronous UX Loop:** Engineered entirely around `asyncio` events, wrapping standard blocking input routines with an executor loop so messages flow inbound smoothly without locking your input stream.
4. **Dynamic Terminal UI:** Enhanced with `colorama` ANSI styling formatting to visually segment message streams, system connection alerts, and server-side room presence activities seamlessly inside your shell.
5. **Token Auth Integration:** Seamlessly talks back to the central `ghost-protocol-server` architecture via `httpx` to dynamically trade cryptographic credentials for ephemeral, capability-scoped server permissions.

<hr>

## 3. 🚦 Getting Started

### 💻 Local Development & Execution

Ensure you have **Python 3.10+** installed on your machine.

1.  **Download & Install:** Clone the repository via Git or download and extract the source ZIP file.

    ```bash
    git clone https://github.com/anikethchavare/ghost-protocol-client.git
    cd ghost-protocol-client
    pip install -r requirements.txt
    ```

2. **Verify Server Endpoint:** Ensure the `SERVER_URL` variable inside `app.py` is pointed towards your token provisioning API location. By default, it targets the public server:

    ```python
    SERVER_URL = "https://ghost-protocol.anikethchavare.com/generate-token"
    ```

3.  **Launch**:
    ```bash
    python app.py
    ```

<hr>

## 4. 📜 License & Changelog

This project is licensed under the **[Apache License 2.0](https://github.com/anikethchavare/ghost-protocol-client/blob/main/LICENSE.txt)**. You are free to use, modify, and distribute this software for both commercial and non-commercial purposes, provided original copyright notices and attributions are retained.

Track all notable changes, migrations, and bug fixes in the **[CHANGELOG.md](https://github.com/anikethchavare/ghost-protocol-client/blob/main/CHANGELOG.md)**. This project adheres to Semantic Versioning.

<hr>

## 5. 🤝 Credits & Acknowledgements

This project is made possible by the incredible work of the open-source cryptography and real-time networking communities. A comprehensive list of project client dependencies and their respective licenses is available in **[CREDITS.md](https://github.com/anikethchavare/ghost-protocol-client/blob/main/CREDITS.md)**.

<hr>

## 6. 💎 Become a Sponsor

**Ghost Protocol** is built and maintained entirely for open-source privacy and security architecture research. If this utility helps power your personal network experiments or inspires your cryptographic terminal interfaces, please consider supporting its continuous development.

Your sponsorship helps offset the overhead of running live end-to-end sandbox channels, public test infrastructure, and edge routing logic globally.

<br>

<div align="center">
    <a href="https://github.com/sponsors/anikethchavare">
        <img src="https://img.shields.io/badge/Sponsor_on_GitHub-EA4AAA?style=for-the-badge&logo=github-sponsors&logoColor=white" alt="Sponsor on GitHub">
    </a>
</div>

<hr>

## 7. ✨ Conclusion

Thank you for exploring **Ghost Protocol (Client)**. Whether you want to tinker with the terminal layout or implement your own custom session key rotation mechanisms, feel free to fork the repository.

If you encounter any issues or want to patch up any of the known alpha limitations listed above, please open an issue or submit a pull request.