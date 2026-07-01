<div align="center"><h1>anikethchavare // Ghost Protocol (Client)</h1></div>
<div align="center"><strong>This is the client application of Ghost Protocol, an end-to-end encrypted (E2EE) terminal chat application built <br> with Python and WebSockets, routing communications securely without leaving a trace.</strong></div>

<br>

<div align="center"><img width="575" alt="Main Image for README (Terminal)" src="https://github.com/user-attachments/assets/b848b2aa-5c0a-43ff-b35e-d9dff691a687"></div>

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
    <img src="https://img.shields.io/badge/version-0.2.0-blue?style=for-the-badge&logo=github&logoColor=white" alt="Version">&nbsp;&nbsp;
    <img src="https://img.shields.io/badge/license-Apache_2.0-blue?style=for-the-badge&logo=apache&logoColor=white" alt="Apache 2.0 License">&nbsp;&nbsp;
    <img src="https://img.shields.io/badge/maintained-yes-brightgreen?style=for-the-badge&logo=checkmarx&logoColor=white" alt="Maintenance: Active">
</div>

<hr>

## 1. ⚠️ Important Status: Unstable Release (v0.1.0)

This release is a highly functional demonstration of asynchronous E2EE communication over a real-time pub/sub network. It is **not** currently audited or hardened for production environments.

### Known Limitations (Fixes slated for v1.0.0):
1. **No Forward Secrecy:** Room session keys are static per session lifecycle and do not rotate when members leave or join.
2. **Insecure Roster Validation:** Username uniqueness and channel presence validation are handled entirely on the client side. A secure deployment must offload roster validation to a trusted backend authority to prevent spoofing. 

*Do not use this version to transmit highly sensitive information or real production secrets.*

<hr>

## 2. 🛠️ Features & Tech Stack

This lightweight CLI script serves as the interactive frontend interface for the **Ghost Protocol** room-based chat application.

1. **End-to-End Encryption & Anti-Replay Protection:** Uses modern, industry-standard cryptographic primitives featuring `X25519` for peer-to-peer key handshakes, `HKDF` for ephemeral key derivation, and `AES-256-GCM` for authenticated data packet encryption. Payloads are reinforced with strict temporal verification windows to entirely mitigate message replay attacks.
2. **Randomized Client Identities:** Hardened against user tracking and session spoofing by leveraging completely unpredictable `UUIDv4` identifiers for runtime identity generation instead of deterministic values.
3. **Real-Time Mesh Pub/Sub & Host Election:** Driven by the [Ably Python SDK](https://github.com/ably/ably-python) to handle multiplexed, low-latency room communication streams concurrently. Includes a deterministic host election protocol using active room presence rosters to eliminate handshake race conditions during session key delivery.
4. **Asynchronous UX Loop:** Engineered entirely around `asyncio` events, wrapping standard blocking input routines with an executor loop so messages flow inbound smoothly without locking your input stream.
5. **Dynamic Terminal UI:** Enhanced with `colorama` ANSI styling formatting to visually segment message streams, system connection alerts, and server-side room presence activities seamlessly inside your shell.
6. **Token Auth Integration:** Seamlessly talks back to the central `ghost-protocol-server` architecture via `httpx` to dynamically trade cryptographic credentials for ephemeral, capability-scoped server permissions.

<hr>

## 3. 🚦 Getting Started

You can run **Ghost Protocol** either as a compiled standalone executable or directly via the raw Python source code.

### 📦 Option A: Compiled Executable (Recommended for Quick Run)

We provide a standalone executable configuration pre-compiled for easy execution without needing a local Python environment setup.

1. **Locate the Executable:** Open the root directory of the project and navigate to the `/dist` folder.
2. **Execute:** Double-click `ghost-protocol.exe` (on Windows) or execute it via your shell to launch the application instantly.

*Note: If you want to build the latest changes into a single executable manually, install the dependencies and run the compilation script below from the repository root. You can choose your preferred visual theme by swapping out the icon name placeholder with `icon-green.ico`, `icon-blue.ico`, or `icon-grey.ico` from the `icons/` directory:*

```bash
pyinstaller --onefile --console --name ghost-protocol --icon=icons/<icon-name>.ico app.py
```

### 💻 Option B: Local Development & Execution

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