# Onju Voice ESPHome

A native ESPHome firmware for the [Onju Voice](https://github.com/justLV/onju-voice) PCB, turning a Google Nest Mini (2nd gen) into a fully functional Home Assistant voice satellite.

Built on native ESPHome components with no external dependencies — works with the latest ESPHome releases.

## Features

- On-device wake word via microWakeWord
- Voice assistant pipeline (wake word → STT → conversation → TTS)
- Voice timers with LED countdown and alarm tone
- Touch controls with LED feedback (volume, tap-to-talk, mute)
- Follow-up conversation without repeating the wake word
- Media player for music and TTS announcements from Home Assistant

## Prerequisites

- [Onju Voice PCB](https://github.com/justLV/onju-voice) installed in a Google Nest Mini 2nd gen
- Home Assistant 2024.7.0 or newer
- ESPHome 2026.3.0 or newer
- A voice assistant pipeline configured in HA with STT and TTS

## Installation

### First time (USB required)

The first flash must be done via USB before assembling the board into the Nest Mini housing.

1. Hold the **BOOT** button on the Onju Voice PCB
2. Connect USB to your computer
3. Go to [web.esphome.io](https://web.esphome.io) and click **Install**
4. Select the firmware `.bin` file (factory format)
5. After flashing, the device creates a WiFi AP named "Onju Voice"
6. Connect to it and enter your WiFi credentials
7. The device should appear in Home Assistant automatically

### Adopting in ESPHome Dashboard

After the device connects to WiFi, it will appear in ESPHome Dashboard. Click **Adopt** and the config will be imported automatically via `dashboard_import`.

### OTA updates

After the first flash, all subsequent updates can be done wirelessly (OTA).

If upgrading from tetele's config (which uses Arduino framework), OTA may fail due to the framework change. In that case, USB flash is required.

### Manual YAML

If you prefer to manage the config manually instead of using `dashboard_import`:

```yaml
substitutions:
  name: my-onju-voice
  friendly_name: Living Room Voice

packages:
  onju_voice: github://idskov/onju-voice-esphome/onju-voice.yaml@master

esphome:
  name: ${name}
  name_add_mac_suffix: false
  friendly_name: ${friendly_name}

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_encryption_key
```

## Hardware limitations

The Onju Voice PCB has a **shared I2S bus** between the microphone and speaker. This means:

- The device cannot listen and play audio simultaneously
- Wake word detection pauses during audio playback
- After playback finishes, wake word detection resumes automatically

This is a hardware limitation of the original PCB design (no separate I2S buses, no XMOS DSP chip). The firmware handles this transparently.

## Controls

| Control | Action |
|---------|--------|
| **Left touch** | Volume down (hold to repeat) |
| **Right touch** | Volume up (hold to repeat) |
| **Center touch** | Push-to-talk / dismiss timer alarm / stop music |
| **Mute switch** | Toggle wake word listening |

## LED states

| Color | Effect | Meaning |
|-------|--------|---------|
| Orange | Slow pulse | Booting, connecting to WiFi |
| Green | Pulse | Connected to WiFi, waiting for HA |
| Purple | Gentle twinkle | Listening for wake word |
| White | Twinkle | Recording your voice |
| Blue | Scan | Processing (STT + LLM) |
| Green | Flicker | Speaking (playing TTS response) |
| Teal | Flicker | Playing media/music |
| Orange | Proportional bar | Timer countdown (shrinks as time passes) |
| Red | Pulse | Timer alarm (touch center to dismiss) |
| White | Proportional | Volume level (2s after adjustment) |
| Off | — | Idle (wake word light disabled) |

## Home Assistant entities

| Entity | Type | Description |
|--------|------|-------------|
| Use Wake Word | Switch | Enable/disable wake word detection |
| Wake Word Listening Light | Switch | Toggle the purple listening LED |
| Music Playback Light | Switch | Toggle the teal LED during music |
| Timer LED | Switch | Show/hide timer countdown bar |
| Disable wake word | Binary sensor | Hardware mute switch state |
| Media Player | Media player | Music playback and TTS announcements |

## Known issues

- **Follow-up timeout**: If you don't respond to a follow-up prompt, background noise may be interpreted as speech, causing an unexpected response. This is a pipeline-side issue, not firmware.
- **TTS latency**: There's a ~5-7 second delay between the LLM response and audio playback while TTS audio is generated and downloaded. Streaming TTS support could reduce this.

## Credits

- [Justin Alvey](https://github.com/justLV) (@justLV) for the excellent Onju Voice PCB
- [Tudor Olariu](https://github.com/tetele) (@tetele) for the original ESPHome config that inspired this work
- The ESPHome and Home Assistant teams for the voice assistant platform
- [Kevin Ahrendt](https://github.com/kahrendt) for microWakeWord

## License

MIT License. See [LICENSE](LICENSE) for details.

The Onju Voice PCB has [its own license](https://github.com/justLV/onju-voice/blob/master/LICENSE).
