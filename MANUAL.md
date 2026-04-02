# Onju Voice — User Manual

Detailed guides for the Onju Voice ESPHome firmware. For installation and project overview, see [README.md](README.md).

## Table of Contents

- [Installation Notes](#installation-notes)
- [Wake Words](#wake-words)
- [Voice Commands](#voice-commands)
- [Alarm Clock](#alarm-clock)
- [Voice Alarm Scheduling](#voice-alarm-scheduling)
- [Timers](#timers)
- [Music Streaming](#music-streaming)
- [Touch Controls](#touch-controls)
- [LED States](#led-states)

## Installation Notes

See [README.md](README.md) for first-time USB flash and ESPHome Dashboard adoption.

### Pre-compiled firmware

Download firmware from [GitHub Releases](https://github.com/Idskov/onju-voice-esphome/releases) — no ESPHome installation needed:

| File | Use |
|------|-----|
| `.factory.bin` | First-time USB flash (includes bootloader + partition table) |
| `.ota.bin` | OTA updates via the device's captive portal |

**OTA via captive portal:**

1. Download the `.ota.bin` from the latest release
2. Connect to the device's WiFi AP (appears when the device can't reach its configured network, or hold BOOT during power-on)
3. Navigate to `192.168.4.1` in your browser
4. Upload the `.ota.bin` file

**OTA via Home Assistant:** If the device is adopted in ESPHome Dashboard, OTA updates are pushed automatically when you compile and install.

### Manual YAML

If you prefer managing the config yourself instead of using `dashboard_import`:

```yaml
substitutions:
  name: my-onju-voice
  friendly_name: Living Room Voice

packages:
  onju_voice: github://idskov/onju-voice-esphome/onju-voice.yaml@main

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

ota:
  - platform: esphome
    password: !secret ota_password
```

> **Note:** If your config references `ref: master`, update it to `ref: main`. The `master` branch is a mirror kept for backward compatibility.

## Wake Words

The firmware ships with two on-device wake word models: **"OK Nabu"** and **"Hey Jarvis"**. Both are loaded simultaneously — whichever is detected first triggers the voice pipeline.

### Selecting wake words in Home Assistant

Each Onju Voice device exposes two wake word slots in the HA device page. Open **Settings → Devices → [your device] → Configure** and use the **Wake word** and **Wake word 2** dropdowns to select which models are active.

Set a slot to "No wake word" to disable it.

### Adding or removing models

Wake word models are defined in the `micro_wake_word` section of the YAML config:

```yaml
micro_wake_word:
  models:
    - model: okay_nabu
    - model: hey_jarvis
```

To change available models, edit the `models` list. ESPHome includes several built-in models (`okay_nabu`, `hey_jarvis`, `hey_mycroft`, `alexa`, etc.). See the [microWakeWord documentation](https://esphome.io/components/micro_wake_word.html) for the full list and instructions for training custom models.

> **Note:** Each additional model increases memory usage and slightly reduces detection accuracy. Two models is a good balance for the ESP32-S3.

### Wake word listening light

The purple twinkle LED indicates that the device is listening for a wake word. Toggle it via the **Wake Word Listening Light** switch in HA.

## Voice Commands

The Onju Voice works with Home Assistant's voice assistant pipeline. After the wake word is detected, speak your command — the device streams audio to HA for processing.

### What works natively

Everything supported by your HA conversation agent:

- **Timers**: "Set a timer for 5 minutes", "Cancel the timer", "How much time is left?"
- **Device control**: "Turn on the kitchen lights", "Set the thermostat to 22 degrees"
- **Conversation**: Whatever your configured LLM/conversation agent supports

### What requires extra setup

- **Alarm scheduling**: "Set alarm to 7:30" — requires HA-side configuration. See [Voice Alarm Scheduling](#voice-alarm-scheduling).

### Follow-up conversation

After the voice assistant responds, you can ask a follow-up without repeating the wake word — just tap the center touch pad. The device enters push-to-talk mode for 15 seconds after each response.

## Alarm Clock

The Onju Voice has a built-in alarm clock with NVS persistence (survives power loss).

### Entities

| Entity | Type | Description | Default |
|--------|------|-------------|---------|
| Alarm Enabled | Switch | Arm/disarm the alarm | Off |
| Alarm Hour | Number (0–23) | Hour in 24h format | 7 |
| Alarm Minute | Number (0–59) | Minute | 0 |
| Alarm Snooze Minutes | Number (1–30) | Snooze duration | 9 |
| Alarm Tone | Select | Alarm sound (10 tones) | Classic Alarm |
| Alarm Dismiss Mode | Select | How to stop the alarm | Touch = snooze, voice = stop |
| Alarm Status | Text sensor | Current state | idle |

### Setting the alarm

**Via HA UI:** Set the hour and minute, then toggle Alarm Enabled on. The device confirms with a green LED flash.

**Via service call:** Call `esphome.<device>_set_alarm` with `hour` and `minute` parameters. This automatically enables the alarm.

**Cancel:** Toggle Alarm Enabled off, or call `esphome.<device>_cancel_alarm`.

### Dismiss modes

| Mode | Short press (center) | Long press (1-5s) | Voice "stop" |
|------|---------------------|--------------------|--------------|
| Touch = snooze, voice = stop | Snooze | — | Dismiss |
| Touch = snooze, hold = stop | Snooze | Dismiss | — |
| Touch = stop | Dismiss | — | — |

### Tones

Classic Alarm, Gentle Rise, Morning Melody, Reveille, Crazy Rooster, Midnight Driveby, Angry Wasp, Funeral March, Drunk Clown, Samba Wake.

### Status sensor

The `Alarm Status` text sensor reports the current state:

| State | Meaning |
|-------|---------|
| `idle` | No alarm set |
| `set:HH:MM` | Alarm armed for HH:MM |
| `ringing` | Alarm is firing |
| `snoozed:HH:MM` | Snoozed, will ring again at HH:MM |

### Priority behavior

When the alarm fires, it takes priority over everything:
- Stops the voice assistant if active
- Dismisses any ringing timer alarm
- Stops media playback
- Wake word detection is paused during the alarm

## Voice Alarm Scheduling

Voice timers ("set a timer for 5 minutes") work out of the box because Home Assistant has 8 native timer intents built into the voice protocol. Alarm clock scheduling has no native support — there are no `HassSetAlarm` or `HassCancelAlarm` intents in HA.

This is a known gap in the HA/ESPHome voice ecosystem. See [#30](https://github.com/Idskov/onju-voice-esphome/issues/30) for upstream context.

### The workaround: HA custom sentences + intent scripts

You can bridge voice commands to the ESPHome alarm services using HA's custom sentence and intent_script features.

**Step 1: Create a custom sentence file**

Create `custom_sentences/en/onju_alarm.yaml` in your HA config directory:

```yaml
language: "en"
intents:
  SetOnjuAlarm:
    data:
      - sentences:
          - "set [the] alarm to {hour}:{minute}"
          - "set [the] alarm for {hour}:{minute}"
          - "wake me [up] at {hour}:{minute}"
  CancelOnjuAlarm:
    data:
      - sentences:
          - "cancel [the|my] alarm"
          - "turn off [the|my] alarm"
          - "disable [the|my] alarm"
```

> **Note:** Replace `en` with your language code for other languages. See [HA custom sentences docs](https://www.home-assistant.io/voice_control/custom_sentences/) for the sentence template syntax.

**Step 2: Add intent scripts to `configuration.yaml`**

```yaml
intent_script:
  SetOnjuAlarm:
    action:
      - action: esphome.onju_voice_XXXX_set_alarm
        data:
          hour: "{{ hour | int }}"
          minute: "{{ minute | int }}"
    speech:
      text: "Alarm set for {{ hour }}:{{ '%02d' | format(minute | int) }}"
  CancelOnjuAlarm:
    action:
      - action: esphome.onju_voice_XXXX_cancel_alarm
    speech:
      text: "Alarm cancelled"
```

Replace `onju_voice_XXXX` with your device's actual service name (find it under **Developer Tools → Actions** in HA).

**Step 3: Restart Home Assistant**

Reload or restart HA to pick up the new sentences and intent scripts.

### Limitations

- The custom sentence templates above use 24-hour format (`{hour}:{minute}`). Supporting natural phrases like "set alarm for 6 AM" requires more complex sentence templates with AM/PM slot handling.
- Each Onju Voice device has its own service name, so multi-device setups need separate intent scripts or templated service calls.

## Timers

Voice timers are natively supported by the HA voice assistant — no extra configuration needed.

### Usage

Just say: "Set a timer for 5 minutes", "Cancel the timer", "How much time is left?", "Pause the timer".

### LED countdown

While a timer is running, the LEDs show an orange progress bar that shrinks as time passes. Toggle this with the **Timer LED Countdown** switch.

### Timer tone

The alarm sound when a timer expires is configurable via the **Timer Tone** select entity. The same 10 tones as the alarm clock are available.

### Dismissing

Tap the center touch pad, or say "cancel the timer" / "stop".

### Status sensor

The `Timer Status` text sensor reports:

| State | Meaning |
|-------|---------|
| `idle` | No active timers |
| `active:MM:SS` | Timer running, MM:SS remaining (shortest timer shown) |
| `ringing` | Timer expired, alarm sounding |

## Music Streaming

The Onju Voice appears as a standard Home Assistant media player. You can stream audio to it from any HA integration that supports media players — Music Assistant, Spotify, TTS, media browser, etc.

### I2S bus limitation

The Onju Voice PCB has a shared I2S bus for the microphone and speaker. This means:

- Wake word detection **pauses** during audio playback
- The device cannot listen and play simultaneously
- When playback stops, wake word detection resumes automatically

### Voice assistant during playback

You can still use the voice assistant while music is playing:

1. **Tap the center touch pad** — music pauses, the device listens for your command
2. **Speak your command** — audio is streamed to HA for processing
3. **TTS response plays** — the assistant's response is played
4. **Music resumes** — playback continues automatically when the pipeline finishes

### Music playback light

The teal LED during music playback can be toggled with the **Music Playback Light** switch.

## Touch Controls

| Control | Action | Context |
|---------|--------|---------|
| **Left touch** | Volume down | Always (hold to repeat) |
| **Right touch** | Volume up | Always (hold to repeat) |
| **Center tap** | Snooze or dismiss | Alarm ringing (depends on dismiss mode) |
| **Center tap** | Dismiss | Timer alarm ringing |
| **Center tap** | Stop | Media playing |
| **Center tap** | Cancel | Voice assistant active |
| **Center tap** | Push-to-talk | Idle |
| **Center long press** (1-5s) | Dismiss alarm | Alarm ringing, "Touch = snooze, hold = stop" mode |
| **Mute switch** | Toggle wake word | Hardware switch (GPIO38) |

The center touch follows a priority cascade: alarm → timer → media → voice → push-to-talk.

## LED States

| Color | Effect | Meaning |
|-------|--------|---------|
| Orange | Slow pulse | Booting / connecting to WiFi |
| Green | Pulse | Connected to WiFi, waiting for HA |
| Purple | Gentle twinkle | Listening for wake word |
| White | Twinkle | Recording your voice |
| Blue | Scan | Processing (STT + LLM) |
| Green | Flicker | Speaking (TTS response) |
| Teal | Flicker | Playing media/music |
| Orange | Proportional bar | Timer countdown |
| Red | Pulse | Timer alarm ringing |
| Red | Fast blink | Alarm clock ringing |
| Green | Flash | Alarm confirmed / snoozed |
| White | Proportional | Volume level (2s after adjustment) |
| Off | — | Idle (wake word light disabled) |

**LED priority** (highest to lowest): Volume → Alarm clock → Timer alarm → Voice pipeline → Media/TTS → Timer countdown → Wake word → Off.
