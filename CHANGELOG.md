# Changelog

## [1.3.0](https://github.com/Idskov/onju-voice-esphome/compare/v1.2.0...v1.3.0) (2026-04-01)


### Features

* add CI/CD pipeline for automated releases ([9559ca5](https://github.com/Idskov/onju-voice-esphome/commit/9559ca557fc763fb0725631be79578d63c853cd8))
* CI/CD pipeline for automated releases ([7391c12](https://github.com/Idskov/onju-voice-esphome/commit/7391c12e5a4ac43c937280bb27f5c81c81da54ff))


### Bug Fixes

* gate handle-stable-result on new_version check ([e8b8f32](https://github.com/Idskov/onju-voice-esphome/commit/e8b8f3265e84e3e165fe479d5317099b7e6aec31))
* release-please config and compat workflow gates ([f4ff11d](https://github.com/Idskov/onju-voice-esphome/commit/f4ff11d595b2e7a40683c3a0eea408bbddda666d))
* use string extra-files for release-please version detection ([de2f9b1](https://github.com/Idskov/onju-voice-esphome/commit/de2f9b1346092b0e19346cf5d1a7897cd36348f0))

## [1.2.0] - 2026-03-31

### Added
- **Voice timers** — proportional LED countdown bar (orange), RTTTL alarm on finish, center touch to dismiss
- Timer LED switch (show/hide countdown)
- RTTTL component with alert_speaker mixer source

### Changed
- LED priority cascade: volume > alarm > voice pipeline > music/announcing > timer countdown > wake word > off
- Voice pipeline LEDs (listening, processing) no longer overwritten by timer tick

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
