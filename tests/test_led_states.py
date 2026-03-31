"""
Onju Voice LED State Machine Simulator

Models the firmware's LED logic and verifies correct LED output
for all combinations of device state. Run with: pytest tests/
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional
import pytest


# --- LED model ---

class LedColor(Enum):
    OFF = "off"
    ORANGE_SLOW_PULSE = "orange/slow_pulse"       # boot, no wifi
    GREEN_PULSE = "green/pulse"                     # wifi ok, no HA
    GREEN_SOLID = "green/solid"                     # connected (brief)
    PURPLE_TWINKLE = "purple/listening_ww"          # idle, WW active
    WHITE_LISTENING = "white/listening"              # voice: recording
    BLUE_PROCESSING = "blue/processing"             # voice: STT+LLM
    GREEN_SPEAKING = "green/speaking"               # TTS announcement
    TEAL_PLAYING = "teal/speaking"                  # media playback
    WHITE_VOLUME = "white/show_volume"              # volume adjust
    RED_ERROR = "red/solid"                         # error
    ORANGE_TIMER = "orange/show_timer"              # timer countdown bar
    RED_ALARM = "red/pulse"                         # timer alarm
    RAINBOW_PLAYING = "rainbow/rainbow"             # party: rainbow
    FIRE_PLAYING = "fire/fire"                      # party: fire
    CHASE_PLAYING = "chase/chase"                   # party: chase
    STROBE_PLAYING = "strobe/strobe"                # party: strobe


class MediaPlayerState(Enum):
    IDLE = auto()
    PLAYING = auto()
    ANNOUNCING = auto()


class VoiceAssistantState(Enum):
    IDLE = auto()
    LISTENING = auto()
    PROCESSING = auto()
    RESPONDING = auto()  # TTS playing via announcement


# --- Device state ---

@dataclass
class DeviceState:
    media_player: MediaPlayerState = MediaPlayerState.IDLE
    voice_assistant: VoiceAssistantState = VoiceAssistantState.IDLE
    showing_volume: bool = False
    mute_switch: bool = False       # True = muted
    use_wake_word: bool = True
    flicker_wake_word: bool = True
    music_led_mode: str = "solid"       # off, solid, rainbow, fire, chase, strobe, cycle
    timer_alarm_active: bool = False
    active_timer_count: int = 0
    volume_sound: bool = True
    timer_led: bool = True
    mic_capturing: bool = False


# --- Firmware logic simulation ---

def reset_led(s: DeviceState) -> LedColor:
    """Simulates the reset_led script from onju-voice.yaml

    Priority: volume > timer_alarm > music > announcing > timer_countdown > wake_word > off
    """
    # 1. Volume always wins
    if s.showing_volume:
        return LedColor.WHITE_VOLUME

    # 2. Timer alarm
    if s.timer_alarm_active:
        return LedColor.RED_ALARM

    # 3. Media playing (party mode)
    if s.media_player == MediaPlayerState.PLAYING:
        mode = s.music_led_mode
        if mode == "off":
            return LedColor.OFF
        elif mode == "solid":
            return LedColor.TEAL_PLAYING
        elif mode == "rainbow" or mode == "cycle":
            return LedColor.RAINBOW_PLAYING
        elif mode == "fire":
            return LedColor.FIRE_PLAYING
        elif mode == "chase":
            return LedColor.CHASE_PLAYING
        elif mode == "strobe":
            return LedColor.STROBE_PLAYING
        else:
            return LedColor.TEAL_PLAYING

    # 4. Announcing (TTS)
    if s.media_player == MediaPlayerState.ANNOUNCING:
        return LedColor.GREEN_SPEAKING

    # 5. Timer countdown
    if s.active_timer_count > 0 and s.timer_led:
        return LedColor.ORANGE_TIMER

    # 6. Wake word idle
    if s.use_wake_word and s.flicker_wake_word and not s.mute_switch:
        return LedColor.PURPLE_TWINKLE

    return LedColor.OFF


def on_listening(s: DeviceState) -> LedColor:
    """Voice assistant enters listening state"""
    return LedColor.WHITE_LISTENING


def on_stt_vad_end(s: DeviceState) -> LedColor:
    """Voice detected end of speech"""
    return LedColor.BLUE_PROCESSING


def on_announcement(s: DeviceState) -> LedColor:
    """Media player starts announcement (TTS response)"""
    # Firmware calls reset_led, which checks media_player state
    s.media_player = MediaPlayerState.ANNOUNCING
    return reset_led(s)


def on_play(s: DeviceState) -> LedColor:
    """Media player starts media playback"""
    s.media_player = MediaPlayerState.PLAYING
    return reset_led(s)


def on_idle_media(s: DeviceState) -> LedColor:
    """Media player returns to idle"""
    s.media_player = MediaPlayerState.IDLE
    return reset_led(s)


def on_error(s: DeviceState) -> LedColor:
    """Voice assistant error — calls reset_led"""
    return reset_led(s)


def on_ptt_timeout(s: DeviceState) -> LedColor:
    """Push-to-talk timeout — stops VA, calls reset_led + start_wake_word"""
    s.voice_assistant = VoiceAssistantState.IDLE
    return reset_led(s)


def volume_adjust(s: DeviceState) -> LedColor:
    """Volume touch pressed"""
    s.showing_volume = True
    return LedColor.WHITE_VOLUME


def volume_timeout(s: DeviceState) -> LedColor:
    """Volume display timeout (2s after touch release)"""
    s.showing_volume = False
    return reset_led(s)


def center_touch(s: DeviceState) -> Optional[LedColor]:
    """Center touch — stops music if playing, else PTT"""
    if s.media_player == MediaPlayerState.PLAYING:
        s.media_player = MediaPlayerState.IDLE
        # on_idle will fire, which calls reset_led
        return reset_led(s)
    elif s.voice_assistant != VoiceAssistantState.IDLE:
        s.voice_assistant = VoiceAssistantState.IDLE
        return None  # on_end fires (empty), on_idle handles LED
    else:
        s.voice_assistant = VoiceAssistantState.LISTENING
        return LedColor.WHITE_LISTENING


# --- Tests ---

class TestResetLed:
    """Test reset_led for all state combinations"""

    def test_volume_always_wins(self):
        """Volume display takes priority over everything"""
        for mp in MediaPlayerState:
            for mute in [True, False]:
                s = DeviceState(media_player=mp, showing_volume=True, mute_switch=mute)
                assert reset_led(s) == LedColor.WHITE_VOLUME, \
                    f"Volume should win over {mp}, mute={mute}"

    def test_playing_with_solid_mode(self):
        s = DeviceState(media_player=MediaPlayerState.PLAYING, music_led_mode="solid")
        assert reset_led(s) == LedColor.TEAL_PLAYING

    def test_playing_with_mode_off(self):
        s = DeviceState(media_player=MediaPlayerState.PLAYING, music_led_mode="off")
        assert reset_led(s) == LedColor.OFF

    def test_announcing(self):
        s = DeviceState(media_player=MediaPlayerState.ANNOUNCING)
        assert reset_led(s) == LedColor.GREEN_SPEAKING

    def test_announcing_beats_wake_word(self):
        """Even with WW active, announcing shows green"""
        s = DeviceState(
            media_player=MediaPlayerState.ANNOUNCING,
            use_wake_word=True, flicker_wake_word=True, mute_switch=False
        )
        assert reset_led(s) == LedColor.GREEN_SPEAKING

    def test_idle_ww_active(self):
        s = DeviceState(use_wake_word=True, flicker_wake_word=True, mute_switch=False)
        assert reset_led(s) == LedColor.PURPLE_TWINKLE

    def test_idle_ww_disabled(self):
        s = DeviceState(use_wake_word=False)
        assert reset_led(s) == LedColor.OFF

    def test_idle_ww_light_off(self):
        s = DeviceState(use_wake_word=True, flicker_wake_word=False, mute_switch=False)
        assert reset_led(s) == LedColor.OFF

    def test_idle_muted(self):
        s = DeviceState(use_wake_word=True, flicker_wake_word=True, mute_switch=True)
        assert reset_led(s) == LedColor.OFF


class TestVoicePipeline:
    """Test LED states through voice assistant flow"""

    def test_ww_to_listening(self):
        s = DeviceState()
        assert on_listening(s) == LedColor.WHITE_LISTENING

    def test_listening_to_processing(self):
        s = DeviceState(voice_assistant=VoiceAssistantState.LISTENING)
        assert on_stt_vad_end(s) == LedColor.BLUE_PROCESSING

    def test_processing_to_speaking(self):
        s = DeviceState(voice_assistant=VoiceAssistantState.PROCESSING)
        assert on_announcement(s) == LedColor.GREEN_SPEAKING

    def test_speaking_to_idle(self):
        s = DeviceState(media_player=MediaPlayerState.ANNOUNCING)
        assert on_idle_media(s) == LedColor.PURPLE_TWINKLE

    def test_full_pipeline_sequence(self):
        """Simulate complete wake word → response → idle"""
        s = DeviceState()

        # Idle: purple
        assert reset_led(s) == LedColor.PURPLE_TWINKLE

        # Wake word detected → listening
        s.voice_assistant = VoiceAssistantState.LISTENING
        assert on_listening(s) == LedColor.WHITE_LISTENING

        # Speech ends → processing
        s.voice_assistant = VoiceAssistantState.PROCESSING
        assert on_stt_vad_end(s) == LedColor.BLUE_PROCESSING

        # TTS starts → announcing
        s.voice_assistant = VoiceAssistantState.RESPONDING
        assert on_announcement(s) == LedColor.GREEN_SPEAKING

        # TTS done → idle
        s.voice_assistant = VoiceAssistantState.IDLE
        assert on_idle_media(s) == LedColor.PURPLE_TWINKLE

    def test_ptt_timeout(self):
        """Push-to-talk with no speech → timeout → idle"""
        s = DeviceState(voice_assistant=VoiceAssistantState.LISTENING)
        assert on_ptt_timeout(s) == LedColor.PURPLE_TWINKLE

    def test_ptt_timeout_muted(self):
        s = DeviceState(voice_assistant=VoiceAssistantState.LISTENING, mute_switch=True)
        assert on_ptt_timeout(s) == LedColor.OFF

    def test_error_returns_to_idle(self):
        s = DeviceState(voice_assistant=VoiceAssistantState.LISTENING)
        assert on_error(s) == LedColor.PURPLE_TWINKLE


class TestMediaPlayback:
    """Test LED states for music playback"""

    def test_play_shows_teal(self):
        s = DeviceState()
        assert on_play(s) == LedColor.TEAL_PLAYING

    def test_stop_returns_to_ww(self):
        s = DeviceState(media_player=MediaPlayerState.PLAYING)
        assert on_idle_media(s) == LedColor.PURPLE_TWINKLE

    def test_stop_returns_to_off_when_muted(self):
        s = DeviceState(media_player=MediaPlayerState.PLAYING, mute_switch=True)
        assert on_idle_media(s) == LedColor.OFF

    def test_center_touch_stops_music(self):
        s = DeviceState(media_player=MediaPlayerState.PLAYING)
        led = center_touch(s)
        assert s.media_player == MediaPlayerState.IDLE
        assert led == LedColor.PURPLE_TWINKLE

    def test_center_touch_stops_music_muted(self):
        s = DeviceState(media_player=MediaPlayerState.PLAYING, mute_switch=True)
        led = center_touch(s)
        assert led == LedColor.OFF


class TestVolumeOverlay:
    """Test volume display overlay behavior"""

    def test_volume_during_idle(self):
        s = DeviceState()
        assert volume_adjust(s) == LedColor.WHITE_VOLUME
        assert volume_timeout(s) == LedColor.PURPLE_TWINKLE

    def test_volume_during_music(self):
        s = DeviceState(media_player=MediaPlayerState.PLAYING)
        assert volume_adjust(s) == LedColor.WHITE_VOLUME
        # After timeout, should return to teal (not purple!)
        assert volume_timeout(s) == LedColor.TEAL_PLAYING

    def test_volume_during_music_mode_off(self):
        s = DeviceState(media_player=MediaPlayerState.PLAYING, music_led_mode="off")
        assert volume_adjust(s) == LedColor.WHITE_VOLUME
        assert volume_timeout(s) == LedColor.OFF

    def test_volume_during_announcing(self):
        s = DeviceState(media_player=MediaPlayerState.ANNOUNCING)
        assert volume_adjust(s) == LedColor.WHITE_VOLUME
        assert volume_timeout(s) == LedColor.GREEN_SPEAKING

    def test_volume_when_muted(self):
        s = DeviceState(mute_switch=True)
        assert volume_adjust(s) == LedColor.WHITE_VOLUME
        assert volume_timeout(s) == LedColor.OFF


class TestMusicInterruption:
    """Test voice assistant interrupting music"""

    def test_ww_during_music(self):
        """Wake word during music → listening → process → speak → resume music"""
        s = DeviceState(media_player=MediaPlayerState.PLAYING)

        # Playing: teal
        assert reset_led(s) == LedColor.TEAL_PLAYING

        # Wake word → listening (media_player still PLAYING but mic takes I2S)
        s.voice_assistant = VoiceAssistantState.LISTENING
        assert on_listening(s) == LedColor.WHITE_LISTENING

        # Processing
        s.voice_assistant = VoiceAssistantState.PROCESSING
        assert on_stt_vad_end(s) == LedColor.BLUE_PROCESSING

        # TTS announcement (media_player switches to ANNOUNCING)
        s.voice_assistant = VoiceAssistantState.RESPONDING
        s.media_player = MediaPlayerState.ANNOUNCING
        assert on_announcement(s) == LedColor.GREEN_SPEAKING

        # TTS done → music resumes
        s.voice_assistant = VoiceAssistantState.IDLE
        s.media_player = MediaPlayerState.PLAYING
        assert on_play(s) == LedColor.TEAL_PLAYING


class TestMuteSwitch:
    """Test mute switch behavior"""

    def test_mute_hides_ww_light(self):
        s = DeviceState(mute_switch=True)
        assert reset_led(s) == LedColor.OFF

    def test_unmute_shows_ww_light(self):
        s = DeviceState(mute_switch=False)
        assert reset_led(s) == LedColor.PURPLE_TWINKLE

    def test_mute_during_music_still_shows_teal(self):
        """Mute affects wake word LED, not media playback LED"""
        s = DeviceState(media_player=MediaPlayerState.PLAYING, mute_switch=True, music_led_mode="solid")
        assert reset_led(s) == LedColor.TEAL_PLAYING


class TestExhaustive:
    """Exhaustive test: every combination must produce a valid LED state"""

    def test_all_combinations(self):
        """No combination of core state should produce an unexpected result"""
        valid_leds = set(LedColor)
        tested = 0
        modes = ["off", "solid", "rainbow", "fire", "chase", "strobe", "cycle"]

        for mp in MediaPlayerState:
            for vol in [True, False]:
                for mute in [True, False]:
                    for ww in [True, False]:
                        for ww_light in [True, False]:
                            for mode in modes:
                                for alarm in [True, False]:
                                    for timer_count in [0, 1]:
                                        s = DeviceState(
                                            media_player=mp,
                                            showing_volume=vol,
                                            mute_switch=mute,
                                            use_wake_word=ww,
                                            flicker_wake_word=ww_light,
                                            music_led_mode=mode,
                                            timer_alarm_active=alarm,
                                            active_timer_count=timer_count,
                                        )
                                        result = reset_led(s)
                                        assert result in valid_leds, \
                                            f"Invalid LED {result} for state {s}"
                                        tested += 1

        # 3 × 2 × 2 × 2 × 2 × 7 × 2 × 2 = 1344
        assert tested == 1344

    def test_priority_order(self):
        """Verify: volume > alarm > playing > announcing > timer_countdown > wake_word > off"""
        s = DeviceState(
            media_player=MediaPlayerState.PLAYING,
            showing_volume=True,
            use_wake_word=True,
            flicker_wake_word=True,
            music_led_mode="rainbow",
            timer_alarm_active=True,
            active_timer_count=1,
        )
        # Volume wins
        assert reset_led(s) == LedColor.WHITE_VOLUME

        # Timer alarm next
        s.showing_volume = False
        assert reset_led(s) == LedColor.RED_ALARM

        # Music next (rainbow mode)
        s.timer_alarm_active = False
        assert reset_led(s) == LedColor.RAINBOW_PLAYING

        # Announcing next
        s.media_player = MediaPlayerState.ANNOUNCING
        assert reset_led(s) == LedColor.GREEN_SPEAKING

        # Timer countdown next
        s.media_player = MediaPlayerState.IDLE
        assert reset_led(s) == LedColor.ORANGE_TIMER

        # Wake word next
        s.active_timer_count = 0
        assert reset_led(s) == LedColor.PURPLE_TWINKLE

        # Off
        s.use_wake_word = False
        assert reset_led(s) == LedColor.OFF
