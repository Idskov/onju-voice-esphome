# Changelog

## [1.2.0] - 2026-03-31

### Added
- **Voice timers** — LED countdown bar (orange), RTTTL alarm on finish, center touch to dismiss
- **Volume click** — short RTTTL tone on volume change (skipped during playback)
- **Party mode** — Music LED Mode select: off, solid, rainbow, fire, chase, strobe, cycle (30s rotation)
- Timer LED switch (show/hide countdown)
- Volume Sound switch (enable/disable click)
- RTTTL component with alert_speaker mixer source

### Changed
- LED priority cascade updated: volume > alarm > music > announcing > timer > wake word > off
- Music Playback Light switch replaced by Music LED Mode select entity

### Removed
- Music Playback Light switch (superseded by Music LED Mode select)

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
