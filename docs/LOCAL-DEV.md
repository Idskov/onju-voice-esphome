# Local Development — Compile & Flash

How to compile and flash firmware to the Onju Voice devices from the local dev environment.

## Devices

| Device | Name | IP | Config (homelab repo) |
|--------|------|-----|----------------------|
| d20 | onju-voice-831d20 | 10.43.0.67 | `esphome/onju-voice-satellite.yaml` |
| d30 | onju-voice-831d30 | 10.43.0.68 | `esphome/onju-voice-831d30.yaml` |

API encryption keys (needed when adding to HA):
- d20: `XwRsRj336SoAv5if5YaME1RT9gGpO1gJGEBU/q8oNvQ=`
- d30: `AoDfqmtMOUkV5WlRM0Y7YFgN/SJc4QqS+B9qaaQiKJY=`

## Architecture

```
onju-voice-esphome repo          homelab repo
┌──────────────────┐            ┌──────────────────────────────────┐
│ onju-voice.yaml  │◄───────────│ esphome/onju-voice-satellite.yaml│ (d20)
│ (base config)    │  packages  │ esphome/onju-voice-831d30.yaml   │ (d30)
└──────────────────┘  ref:master│ esphome/secrets.sops.yaml        │
                                └──────────────────────────────────┘
```

Device configs live in `c:/Projects/personal/homelab/esphome/`. They pull the base config from GitHub via `packages:` with `ref: master` (mirrored from `main` branch automatically).

## Build Host

Compilation runs on **m720q** (10.43.0.41) via SSH. ESPHome is installed in a venv at `/opt/esphome/bin/esphome`.

Windows cannot compile ESP-IDF natively (Git Bash is MSys/Mingw). The build host is required.

## Quick Reference

### Compile + flash one device

```bash
# 1. Decrypt secrets
SOPS="/c/Users/nico/AppData/Local/Microsoft/WinGet/Packages/Mozilla.SOPS_Microsoft.Winget.Source_8wekyb3d8bbwe/sops.exe"
SOPS_AGE_KEY_FILE="/c/Users/nico/AppData/Roaming/sops/age/keys.txt"
SOPS_AGE_KEY_FILE="$SOPS_AGE_KEY_FILE" "$SOPS" -d esphome/secrets.sops.yaml > esphome/secrets.yaml

# 2. Copy config + secrets to build host
scp -i ~/.ssh/claude_homelab esphome/onju-voice-satellite.yaml esphome/secrets.yaml root@10.43.0.41:/tmp/

# 3. Clean local cleartext secrets
rm -f esphome/secrets.yaml

# 4. Clear cached packages (force re-fetch from GitHub)
ssh -i ~/.ssh/claude_homelab root@10.43.0.41 "rm -rf /tmp/.esphome/packages"

# 5. Compile + flash
ssh -i ~/.ssh/claude_homelab root@10.43.0.41 \
  "cd /tmp && /opt/esphome/bin/esphome run onju-voice-satellite.yaml --device 10.43.0.67 --no-logs"
```

Replace config and IP for d30:
- Config: `onju-voice-831d30.yaml`
- IP: `10.43.0.68`

### Compile only (no flash)

```bash
ssh -i ~/.ssh/claude_homelab root@10.43.0.41 \
  "cd /tmp && /opt/esphome/bin/esphome compile onju-voice-satellite.yaml"
```

### Upload only (already compiled)

```bash
ssh -i ~/.ssh/claude_homelab root@10.43.0.41 \
  "cd /tmp && /opt/esphome/bin/esphome upload onju-voice-satellite.yaml --device 10.43.0.67"
```

### Stream logs

```bash
ssh -i ~/.ssh/claude_homelab root@10.43.0.41 \
  "cd /tmp && /opt/esphome/bin/esphome logs onju-voice-satellite.yaml --device 10.43.0.67"
```

## Testing dev branch changes

The device configs pull from GitHub `ref: master`. To test local changes from the `dev` branch before pushing:

### Option A: Override the package reference temporarily

Edit the device config to use a local path instead of the GitHub URL:

```yaml
# Temporary — revert before committing
packages:
  onju_voice: !include /tmp/onju-voice.yaml
```

Then copy your local `onju-voice.yaml` to the build host:

```bash
scp -i ~/.ssh/claude_homelab onju-voice.yaml root@10.43.0.41:/tmp/
```

### Option B: Push to dev and reference it

```yaml
packages:
  onju_voice:
    url: https://github.com/idskov/onju-voice-esphome
    file: onju-voice.yaml
    ref: dev
```

Then clear packages cache and compile as normal.

## Flash both devices

```bash
# Prep
SOPS="/c/Users/nico/AppData/Local/Microsoft/WinGet/Packages/Mozilla.SOPS_Microsoft.Winget.Source_8wekyb3d8bbwe/sops.exe"
SOPS_AGE_KEY_FILE="/c/Users/nico/AppData/Roaming/sops/age/keys.txt"
SOPS_AGE_KEY_FILE="$SOPS_AGE_KEY_FILE" "$SOPS" -d esphome/secrets.sops.yaml > esphome/secrets.yaml
scp -i ~/.ssh/claude_homelab esphome/onju-voice-satellite.yaml esphome/onju-voice-831d30.yaml esphome/secrets.yaml root@10.43.0.41:/tmp/
rm -f esphome/secrets.yaml
ssh -i ~/.ssh/claude_homelab root@10.43.0.41 "rm -rf /tmp/.esphome/packages"

# Flash d20
ssh -i ~/.ssh/claude_homelab root@10.43.0.41 \
  "cd /tmp && /opt/esphome/bin/esphome run onju-voice-satellite.yaml --device 10.43.0.67 --no-logs"

# Flash d30
ssh -i ~/.ssh/claude_homelab root@10.43.0.41 \
  "cd /tmp && /opt/esphome/bin/esphome run onju-voice-831d30.yaml --device 10.43.0.68 --no-logs"
```

## Running tests

pytest hangs on Windows terminal. Use direct Python execution instead:

```bash
cd /c/Projects/personal/onju-voice-esphome
python -c "
from tests.test_led_states import *
from tests.test_state_transitions import *

for mod in [test_led_states, test_state_transitions]:
    for name in dir(mod):
        cls = getattr(mod, name)
        if isinstance(cls, type) and name.startswith('Test'):
            obj = cls()
            for method in dir(obj):
                if method.startswith('test_'):
                    getattr(obj, method)()
            print(f'{name}: OK')

print('ALL TESTS PASS')
"
```

Or target a single test class:

```bash
python -c "
from tests.test_led_states import TestTimerLed, DeviceState, timer_started, LedColor
t = TestTimerLed()
t.test_timer_shows_orange()
t.test_full_timer_lifecycle()
print('OK')
"
```

## Troubleshooting

### OTA upload times out
The device may be unresponsive. Wait 30 seconds and retry — it often works on the second attempt.

### "Speaker buffer full" warnings in logs
Normal when RTTTL and voice pipeline compete for the mixer. The queue_mode handles ordering.

### RTTTL alarm has no sound
MWW must be stopped before RTTTL can play (shared I2S bus). The `timer_alarm` script handles this. If sound is missing, check that `stop_wake_word` runs before `rtttl.play`.

### select.state deprecation warnings
Use `.current_option()` instead of `.state` on select entities. Will become an error in ESPHome 2026.7.0.

### random() compile error
ESP-IDF uses `random()` (no arguments). Use `random() % N` for a range — Arduino-style `random(min, max)` won't compile.

### Device shows duplicate in HA
Delete all Onju Voice entries from HA, reflash, and let mDNS rediscover them.
