# Changelog

All notable changes to Júpiter Product Design Flow are documented here.

## [1.1.2] - 2026-07-17

### Security

- Disable page-authored JavaScript before navigation and use trusted controller evaluation for slide selection and readiness.
- Keep HTTP and WebSocket routes blocked as defense in depth; real-browser tests prove zero HTTP, WebSocket and WebRTC/STUN egress to local listeners.
- Constrain generated files and ZIP outputs to the project tree, including symlink-aware checks.
- Remove the shared temporary HTML injection path and publish generated artifacts through isolated temporary files.

### Reliability

- Pin the Python and Node runtime dependencies used by carousel export.
- Add deterministic local install and verification commands.
- Test Python 3.11 and 3.12 on both macOS and Ubuntu in CI.
- Add a real Chromium smoke test for the Python-to-Playwright export path.

### Compatibility

- Map companion workflows to skills that are available in the current Júpiter agent stack.

## [1.1.1] - 2026-07-15

- Add the editorial carousel production route and artifact contract.
