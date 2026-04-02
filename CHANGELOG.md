# Changelog

## [1.4.0](https://github.com/Idskov/onju-voice-esphome/compare/v1.3.1...v1.4.0) (2026-04-02)


### Features

* add timer status sensor, rename Timer LED ([1f08bfb](https://github.com/Idskov/onju-voice-esphome/commit/1f08bfb3579df3ab4aeb54f4d76fb4fcaad0babd))
* **alarm:** add alarm clock to LED priority cascade ([1fb63e3](https://github.com/Idskov/onju-voice-esphome/commit/1fb63e3085a172f8127ee7dfaf588c7aac66cf5b))
* **alarm:** add all alarm entities and scripts ([f13798d](https://github.com/Idskov/onju-voice-esphome/commit/f13798d2c91992e0d359834c35f2af59f329559f))
* **alarm:** add foundation — globals, time sync, status sensor ([3606fac](https://github.com/Idskov/onju-voice-esphome/commit/3606fac1422bc1621ad54bcad1f39a4109f6c7d3))
* **alarm:** add selectable timer tone ([#15](https://github.com/Idskov/onju-voice-esphome/issues/15)) ([7c1f322](https://github.com/Idskov/onju-voice-esphome/commit/7c1f32273fa2cb4f5bcac967b6074f6bd7336599))
* **alarm:** add time trigger and ESPHome services ([85e2db3](https://github.com/Idskov/onju-voice-esphome/commit/85e2db3713da612e127eaf3b41f01100f3762b22))
* **alarm:** finalize RTTTL alarm tone library ([2ec8df1](https://github.com/Idskov/onju-voice-esphome/commit/2ec8df1d1c98962ca5067cf2b93b529b4d27b6bc))
* **alarm:** update center touch cascade with alarm snooze/dismiss ([1a9e149](https://github.com/Idskov/onju-voice-esphome/commit/1a9e1497b6a3dfe7b68508a11a60cb69f70df7a3))


### Bug Fixes

* **alarm:** cast service params to int for std::min/std::max ([1bfcef5](https://github.com/Idskov/onju-voice-esphome/commit/1bfcef56cb84926579e87e2e4e6c1e00c96e6db9))
* **alarm:** delayed NVS flush for reliable power loss survival ([458fb20](https://github.com/Idskov/onju-voice-esphome/commit/458fb20d49c55df3745cb789b63629fb175539ff))
* **alarm:** flush NVS on each number change, not just alarm_confirm ([d724afd](https://github.com/Idskov/onju-voice-esphome/commit/d724afd90a9cb8019775f66253d605797f238cb4))
* **alarm:** force NVS flush on alarm changes for power loss survival ([626ed13](https://github.com/Idskov/onju-voice-esphome/commit/626ed1319f6fea621699f3ac827028d4e1033471))
* **alarm:** long press dismiss also works during snooze ([74a6dac](https://github.com/Idskov/onju-voice-esphome/commit/74a6dac836cd7798131f3592509a0f6fddbfbdd2))
* **alarm:** number inputs as box mode, clearer dismiss mode labels ([976b0a5](https://github.com/Idskov/onju-voice-esphome/commit/976b0a5b2931af7e8100c93b598175daa3d91a4c))
* clear LED effect on alarm dismiss/snooze and VA cancel ([2a94669](https://github.com/Idskov/onju-voice-esphome/commit/2a94669f47d45aa8d3f8715ec69b4d5784981cd4))
* compat workflow YAML syntax ([e8a167d](https://github.com/Idskov/onju-voice-esphome/commit/e8a167d7d411409ad053c0d73b6b482b804aa3b0))
* rename shadowed variable in timer_tick lambda ([c897460](https://github.com/Idskov/onju-voice-esphome/commit/c8974601e319ab80ea29262c7ca78fe3b12a88a6))
* rewrite compat workflow — fix YAML multiline body strings ([f9a016f](https://github.com/Idskov/onju-voice-esphome/commit/f9a016f83d57ce1a26488294420664f09ae025b5))
* set initial state for timer and alarm status sensors ([6dd8bdc](https://github.com/Idskov/onju-voice-esphome/commit/6dd8bdc23c052ce75bd140e1307939245d4bf5e8))

## [1.3.1](https://github.com/Idskov/onju-voice-esphome/compare/v1.3.0...v1.3.1) (2026-04-01)


### Bug Fixes

* firmware build + release workflow consolidation ([4ba1b66](https://github.com/Idskov/onju-voice-esphome/commit/4ba1b669bc73ca3d33a8e49f2352068268c4aa45))
* move firmware build into release workflow ([d7c6de9](https://github.com/Idskov/onju-voice-esphome/commit/d7c6de9603ab746e5bbfa3b7c7d6d899ebbbf5f7))

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
