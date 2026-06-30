# Changelog

This is the changelog file of `ghost-protocol-client`. All notable changes to
this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The format will be:
- Added
- Changed
- Fixed
- Removed
- Security
- Refactored
- Performance
- Documentation

## [Unreleased]

### Added
- Added a custom terminal title via the `set_terminal_title()` function in `modules/utils.py`.
- Integrated a sleek, stealth-themed `ghost` application icon into the final build configurations.
- Added a dedicated `/icons` directory featuring three distinct style variations for compilation: `icon-green.ico`, `icon-blue.ico`, and `icon-grey.ico`.

### Refactored
- Modularized the codebase by decoupling core cryptography and terminal utilities into dedicated modules for improved readability and maintenance.

### Documentation
- Updated the content of the `README.md` file with the new build instructions.

## [0.2.0] - 2026-06-30

### Changed
- Modified the alert message when a user leaves a room.
- Added a dependency `pyinstaller`.

### Fixed
- Fixed an issue where the executable would instantly close on exit or errors by trapping all termination signals and adding a final terminal-lock prompt.

### Security
- Switched client identity generation from deterministic UUIDv5 to random UUIDv4, preventing identity prediction, tracking, and unauthorized session key spoofing.

### Documentation
- Updated the formatting and content of the `README.md` file.

## [0.1.0] - 2026-06-29

### Added
- Initial project setup for `Ghost Protocol (Client)`.
- Implemented real-time messaging and channel synchronization using `AblyRealtime`.
- Integrated `cryptography` primitives utilizing X25519 for key exchange, HKDF for key derivation, and AES-256-GCM for authenticated symmetric encryption.
- Created an asynchronous terminal loop utilizing `asyncio` and `loop.run_in_executor` to handle concurrent user inputs alongside live sub/pub event processing.
- Added terminal presence management via `Ably` to broadcast member entries, leaves, and connection state changes.
- Integrated `colorama` styling to visually partition messages, presence alerts, system logs, and security warnings in the command-line interface.
- Added client-side runtime unique ID generation leveraging deterministic UUIDv5 formatting.

### Documentation
- Finished the `README.md` file.

---
[0.2.0]: https://github.com/anikethchavare/ghost-protocol-client/releases/tag/v0.2.0
[0.1.0]: https://github.com/anikethchavare/ghost-protocol-client/releases/tag/v0.1.0