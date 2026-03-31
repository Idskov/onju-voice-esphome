# Changelog

## [1.1.0] - 2026-03-31

### Added
- **Media playback** — music and audio from HA media browser, Music Assistant, etc.
  - Mixer speaker architecture with separate announcement and media pipelines
  - Queue mode ensures clean handoff between TTS and media
  - `on_play` LED indicator (teal) distinguishes media from TTS (green)
- `task_stack_in_psram` for media player to reduce RAM pressure
- `volume_increment`, `volume_min`, `volume_max` settings on media player

## [1.0.0] - 2026-03-31

Initial release. Native ESPHome config replacing the abandoned tetele/gnumpi stack.

### Features
- On-device wake word (microWakeWord: okay_nabu, hey_jarvis)
- Voice assistant pipeline (wake word, STT, conversation, TTS)
- Touch volume controls with Nest Mini-style LED feedback
- Hardware mute switch support
- LED states for boot, WiFi, listening, processing, speaking
- Follow-up conversation support
- TTS announcement playback
- Configurable noise suppression level (0-4) via HA entity
- Wake word listening light toggle
- Dashboard import support
