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
[0.1.0]: https://github.com/anikethchavare/ghost-protocol-client/releases/tag/v0.1.0