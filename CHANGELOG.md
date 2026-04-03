# Changelog

## [1.4.0](https://github.com/Idskov/onju-voice-esphome/compare/v1.3.1...v1.4.0) (2026-04-03)


### Features

* add disable_firmware_update substitution for encrypted setups ([a37a2de](https://github.com/Idskov/onju-voice-esphome/commit/a37a2de3fe11e2700a9e5481e20198bac317c165))
* add firmware update system with stable/beta channels ([87b795a](https://github.com/Idskov/onju-voice-esphome/commit/87b795ae561a9efd9e9cfad312c965c2d77a5ab3)), closes [#24](https://github.com/Idskov/onju-voice-esphome/issues/24)
* add timer status sensor, rename Timer LED ([9d7e9bb](https://github.com/Idskov/onju-voice-esphome/commit/9d7e9bbb6c9260bcb81f543e4050944a8ba5dd80))
* **alarm:** add alarm clock to LED priority cascade ([c3dd37f](https://github.com/Idskov/onju-voice-esphome/commit/c3dd37fa46a2e2af08981d331cfee4e690357891))
* **alarm:** add all alarm entities and scripts ([5af362f](https://github.com/Idskov/onju-voice-esphome/commit/5af362fde85a3984163e7ea93d480f6a4d360335))
* **alarm:** add foundation — globals, time sync, status sensor ([a185565](https://github.com/Idskov/onju-voice-esphome/commit/a185565fd79ad505fb9d8193281e0fbc0efb633a))
* **alarm:** add selectable timer tone ([#15](https://github.com/Idskov/onju-voice-esphome/issues/15)) ([878107e](https://github.com/Idskov/onju-voice-esphome/commit/878107eef0a2ef6e516a490b78089ee1a378a172))
* **alarm:** add time trigger and ESPHome services ([bec8926](https://github.com/Idskov/onju-voice-esphome/commit/bec89269897ca55cc094f42fc383205f70c2c334))
* **alarm:** finalize RTTTL alarm tone library ([5e1a47d](https://github.com/Idskov/onju-voice-esphome/commit/5e1a47d79337c5f1eff821078ff3027d160f37df))
* **alarm:** update center touch cascade with alarm snooze/dismiss ([f5f9645](https://github.com/Idskov/onju-voice-esphome/commit/f5f96452510be67d437634bbfc561b8540c1a303))
* **ci:** auto-bump dev version in beta workflow ([27747c7](https://github.com/Idskov/onju-voice-esphome/commit/27747c7e8ae114bb7be869f1899bc5751b4af877))


### Bug Fixes

* **alarm:** cast service params to int for std::min/std::max ([8ad617e](https://github.com/Idskov/onju-voice-esphome/commit/8ad617e249a8ad208ec90f9e061cb94dbb1a4596))
* **alarm:** delayed NVS flush for reliable power loss survival ([9962fc4](https://github.com/Idskov/onju-voice-esphome/commit/9962fc46a73fcc97e0c363e2aa3c9914659fdf1c))
* **alarm:** flush NVS on each number change, not just alarm_confirm ([6a02349](https://github.com/Idskov/onju-voice-esphome/commit/6a023490d5961102c6df804666372531edbe81f5))
* **alarm:** force NVS flush on alarm changes for power loss survival ([d8cd76e](https://github.com/Idskov/onju-voice-esphome/commit/d8cd76e9b67dcf5d71531700d0f836c52ee18a1e))
* **alarm:** long press dismiss also works during snooze ([24a9e8f](https://github.com/Idskov/onju-voice-esphome/commit/24a9e8f4ae65ca006e29b354ff9524cf82f6c222))
* **alarm:** number inputs as box mode, clearer dismiss mode labels ([4e80265](https://github.com/Idskov/onju-voice-esphome/commit/4e802650cbaacaef293b5b94ab3bde6551cd4715))
* **ci:** add workflow_dispatch trigger to beta workflow ([096f2cb](https://github.com/Idskov/onju-voice-esphome/commit/096f2cb2f27ce4310172bbe2f3382c8ddf3d61b0))
* **ci:** split beta workflow into build + release jobs ([a98d4b6](https://github.com/Idskov/onju-voice-esphome/commit/a98d4b6e1ceb485ba4805c8605278d3980b15536))
* clear LED effect on alarm dismiss/snooze and VA cancel ([90f4379](https://github.com/Idskov/onju-voice-esphome/commit/90f4379f77507130f3132929d499e474b6041345))
* compat workflow YAML syntax ([05aadf8](https://github.com/Idskov/onju-voice-esphome/commit/05aadf808e3ddbfb496ed0bcb41ea609115edb4c))
* increase http_request buffer for GitHub redirect headers ([2a9dbad](https://github.com/Idskov/onju-voice-esphome/commit/2a9dbada6bf66b0d7bdc3ea55df7173908a94e2d))
* rename shadowed variable in timer_tick lambda ([d34187f](https://github.com/Idskov/onju-voice-esphome/commit/d34187f2d03a19b69ac3591203d38fbcd0a88dfb))
* rewrite compat workflow — fix YAML multiline body strings ([d4e25ae](https://github.com/Idskov/onju-voice-esphome/commit/d4e25aeda5edbaa927e32a2fca1d2fe19014986e))
* set initial state for timer and alarm status sensors ([4370871](https://github.com/Idskov/onju-voice-esphome/commit/437087108832e87b5beaa920ddf0700c7e230b12))
* set min_version to 2026.2.0 (actual minimum) ([30eba03](https://github.com/Idskov/onju-voice-esphome/commit/30eba03a7a9d748188a9c11015eeed114218334b))

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
