"""
Onju Voice State Transition Tests

Models valid state transitions and verifies:
- Media player state machine (idle/playing/announcing)
- Voice assistant state machine (idle/listening/processing/responding)
- Wake word control (when MWW starts/stops)
- I2S bus arbitration (mic XOR speaker)
- Center touch behavior per state

Run with: pytest tests/
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, List
import pytest


# --- State enums ---

class MediaPlayerState(Enum):
    IDLE = auto()
    PLAYING = auto()
    ANNOUNCING = auto()


class VoiceAssistantState(Enum):
    IDLE = auto()
    LISTENING = auto()
    PROCESSING = auto()
    RESPONDING = auto()


class MWWState(Enum):
    RUNNING = auto()
    STOPPED = auto()


class I2SUser(Enum):
    NONE = auto()
    MICROPHONE = auto()
    SPEAKER = auto()


# --- Device model ---

@dataclass
class Device:
    media_player: MediaPlayerState = MediaPlayerState.IDLE
    voice_assistant: VoiceAssistantState = VoiceAssistantState.IDLE
    mww: MWWState = MWWState.STOPPED
    i2s_user: I2SUser = I2SUser.NONE
    mute_switch: bool = False
    use_wake_word: bool = True
    mic_capturing: bool = False
    log: List[str] = None
    timer_alarm_active: bool = False
    active_timer_count: int = 0

    def __post_init__(self):
        if self.log is None:
            self.log = []

    def _log(self, msg: str):
        self.log.append(msg)

    # --- Scripts (match firmware) ---

    def start_wake_word(self):
        if not self.mute_switch and self.use_wake_word:
            self.mww = MWWState.RUNNING
            self._log("mww.start")

    def stop_wake_word(self):
        self.mww = MWWState.STOPPED
        self._log("mww.stop")

    # --- Triggers ---

    def on_client_connected(self):
        """HA API connected"""
        self._log("on_client_connected")
        self.start_wake_word()

    def on_wake_word_detected(self):
        """MWW detects wake word"""
        self._log("on_wake_word_detected")
        self.voice_assistant = VoiceAssistantState.LISTENING
        self.mww = MWWState.STOPPED
        self.i2s_user = I2SUser.MICROPHONE
        self.mic_capturing = True

    def on_listening(self):
        """VA enters listening state"""
        self._log("on_listening")
        self.voice_assistant = VoiceAssistantState.LISTENING

    def on_stt_vad_end(self):
        """Speech detected, processing begins"""
        self._log("on_stt_vad_end")
        self.voice_assistant = VoiceAssistantState.PROCESSING
        self.mic_capturing = False
        self.i2s_user = I2SUser.NONE

    def on_tts_response(self):
        """TTS announcement starts playing"""
        self._log("on_announcement")
        self.voice_assistant = VoiceAssistantState.RESPONDING
        self.media_player = MediaPlayerState.ANNOUNCING
        self.i2s_user = I2SUser.SPEAKER
        # Firmware: if mic capturing, stop wake word
        if self.mic_capturing:
            self.stop_wake_word()

    def on_va_end(self):
        """Voice assistant pipeline ends (data sent, NOT speaker done)"""
        self._log("on_end")
        # Firmware: empty [] — does nothing

    def on_va_error(self):
        """Voice assistant error"""
        self._log("on_error")
        self.voice_assistant = VoiceAssistantState.IDLE
        self.start_wake_word()

    def on_media_idle(self):
        """Media player finishes playback (speaker done)"""
        self._log("on_idle")
        self.media_player = MediaPlayerState.IDLE
        self.i2s_user = I2SUser.NONE
        self.voice_assistant = VoiceAssistantState.IDLE
        self.start_wake_word()

    def on_play_media(self):
        """External media playback starts"""
        self._log("on_play")
        self.media_player = MediaPlayerState.PLAYING
        self.i2s_user = I2SUser.SPEAKER
        if self.mic_capturing:
            self.stop_wake_word()
            self.mic_capturing = False

    def on_media_stop(self):
        """Media playback stopped (center touch or HA service)"""
        self._log("on_media_stop")
        self.media_player = MediaPlayerState.IDLE
        self.i2s_user = I2SUser.NONE
        self.start_wake_word()

    def center_touch(self):
        """Center touch button pressed"""
        self._log("center_touch")
        if self.timer_alarm_active:
            self.dismiss_alarm()
        elif self.media_player == MediaPlayerState.PLAYING:
            self.on_media_stop()
        elif self.voice_assistant != VoiceAssistantState.IDLE:
            self.voice_assistant = VoiceAssistantState.IDLE
            self.mic_capturing = False
        else:
            # Push-to-talk
            self.voice_assistant = VoiceAssistantState.LISTENING
            self.i2s_user = I2SUser.MICROPHONE
            self.mic_capturing = True

    def ptt_timeout(self):
        """Push-to-talk 15s timeout"""
        self._log("ptt_timeout")
        self.voice_assistant = VoiceAssistantState.IDLE
        self.i2s_user = I2SUser.NONE
        self.mic_capturing = False
        self.start_wake_word()

    def toggle_mute(self, muted: bool):
        """Hardware mute switch toggled"""
        self._log(f"mute={'on' if muted else 'off'}")
        self.mute_switch = muted
        if muted:
            self.stop_wake_word()
        else:
            self.start_wake_word()

    def on_timer_started(self):
        """Voice assistant timer started"""
        self._log("on_timer_started")
        self.active_timer_count += 1

    def on_timer_finished(self):
        """Voice assistant timer finished"""
        self._log("on_timer_finished")
        self.active_timer_count = max(0, self.active_timer_count - 1)
        self.timer_alarm_active = True

    def on_timer_cancelled(self):
        """Voice assistant timer cancelled"""
        self._log("on_timer_cancelled")
        self.active_timer_count = max(0, self.active_timer_count - 1)

    def dismiss_alarm(self):
        """Center touch or HA dismisses alarm"""
        self._log("dismiss_alarm")
        self.timer_alarm_active = False


# --- State transition tests ---

class TestVoicePipelineTransitions:
    """Verify valid state transitions through voice assistant flow"""

    def test_full_wake_word_flow(self):
        d = Device()
        d.on_client_connected()
        assert d.mww == MWWState.RUNNING

        d.on_wake_word_detected()
        assert d.voice_assistant == VoiceAssistantState.LISTENING
        assert d.mww == MWWState.STOPPED
        assert d.i2s_user == I2SUser.MICROPHONE

        d.on_listening()
        assert d.voice_assistant == VoiceAssistantState.LISTENING

        d.on_stt_vad_end()
        assert d.voice_assistant == VoiceAssistantState.PROCESSING
        assert d.i2s_user == I2SUser.NONE

        d.on_tts_response()
        assert d.voice_assistant == VoiceAssistantState.RESPONDING
        assert d.media_player == MediaPlayerState.ANNOUNCING
        assert d.i2s_user == I2SUser.SPEAKER

        d.on_va_end()
        # on_end is empty — state unchanged
        assert d.voice_assistant == VoiceAssistantState.RESPONDING

        d.on_media_idle()
        assert d.voice_assistant == VoiceAssistantState.IDLE
        assert d.media_player == MediaPlayerState.IDLE
        assert d.mww == MWWState.RUNNING
        assert d.i2s_user == I2SUser.NONE

    def test_error_recovery(self):
        d = Device()
        d.on_client_connected()
        d.on_wake_word_detected()
        d.on_listening()
        assert d.mww == MWWState.STOPPED

        d.on_va_error()
        assert d.voice_assistant == VoiceAssistantState.IDLE
        assert d.mww == MWWState.RUNNING

    def test_ptt_timeout_recovery(self):
        d = Device()
        d.on_client_connected()
        d.center_touch()  # start PTT
        assert d.voice_assistant == VoiceAssistantState.LISTENING
        # MWW still "running" in model — in firmware, voice_assistant.start
        # takes over the mic and MWW stops implicitly. The model doesn't
        # simulate this low-level I2S arbitration, but on_listening will
        # fire and the mic is captured.
        assert d.mic_capturing is True

        d.ptt_timeout()
        assert d.voice_assistant == VoiceAssistantState.IDLE
        assert d.mww == MWWState.RUNNING


class TestMediaPlaybackTransitions:

    def test_play_and_stop(self):
        d = Device()
        d.on_client_connected()
        assert d.mww == MWWState.RUNNING

        d.on_play_media()
        assert d.media_player == MediaPlayerState.PLAYING
        assert d.i2s_user == I2SUser.SPEAKER

        d.on_media_stop()
        assert d.media_player == MediaPlayerState.IDLE
        assert d.mww == MWWState.RUNNING

    def test_center_touch_stops_music(self):
        d = Device()
        d.on_client_connected()
        d.on_play_media()
        assert d.media_player == MediaPlayerState.PLAYING

        d.center_touch()
        assert d.media_player == MediaPlayerState.IDLE
        assert d.mww == MWWState.RUNNING

    def test_center_touch_during_idle_starts_ptt(self):
        d = Device()
        d.on_client_connected()
        d.center_touch()
        assert d.voice_assistant == VoiceAssistantState.LISTENING
        assert d.i2s_user == I2SUser.MICROPHONE


class TestMusicInterruptedByVoice:

    def test_wake_word_during_music(self):
        """Music playing → wake word → voice pipeline → music resumes"""
        d = Device()
        d.on_client_connected()
        d.on_play_media()
        assert d.media_player == MediaPlayerState.PLAYING

        # Wake word triggers (HA stops music, starts VA)
        d.on_wake_word_detected()
        assert d.voice_assistant == VoiceAssistantState.LISTENING
        assert d.i2s_user == I2SUser.MICROPHONE

        d.on_stt_vad_end()
        assert d.voice_assistant == VoiceAssistantState.PROCESSING

        # TTS response plays
        d.on_tts_response()
        assert d.media_player == MediaPlayerState.ANNOUNCING

        # TTS done → idle
        d.on_media_idle()
        assert d.voice_assistant == VoiceAssistantState.IDLE
        assert d.mww == MWWState.RUNNING

        # Music resumes (HA re-sends play_media)
        d.on_play_media()
        assert d.media_player == MediaPlayerState.PLAYING


class TestI2SBusArbitration:
    """Verify mic and speaker never claim I2S simultaneously"""

    def _assert_no_conflict(self, d: Device):
        """Mic and speaker must not both be active"""
        if d.mic_capturing:
            assert d.i2s_user == I2SUser.MICROPHONE, \
                f"Mic capturing but I2S user is {d.i2s_user}"
        if d.i2s_user == I2SUser.SPEAKER:
            assert not d.mic_capturing, \
                "Speaker active but mic still capturing"

    def test_voice_pipeline_no_conflict(self):
        d = Device()
        d.on_client_connected()
        self._assert_no_conflict(d)

        d.on_wake_word_detected()
        self._assert_no_conflict(d)  # mic active

        d.on_stt_vad_end()
        self._assert_no_conflict(d)  # neither

        d.on_tts_response()
        self._assert_no_conflict(d)  # speaker active

        d.on_media_idle()
        self._assert_no_conflict(d)  # neither

    def test_music_no_conflict(self):
        d = Device()
        d.on_play_media()
        self._assert_no_conflict(d)  # speaker

        d.on_media_stop()
        self._assert_no_conflict(d)  # neither

    def test_play_stops_mic(self):
        """If mic is capturing when music starts, mic must stop"""
        d = Device()
        d.on_client_connected()
        d.on_wake_word_detected()
        assert d.mic_capturing is True

        d.on_play_media()
        assert d.mic_capturing is False
        assert d.i2s_user == I2SUser.SPEAKER


class TestWakeWordControl:
    """Verify MWW starts and stops at correct times"""

    def test_starts_on_client_connect(self):
        d = Device()
        d.on_client_connected()
        assert d.mww == MWWState.RUNNING

    def test_stops_on_wake_word(self):
        d = Device()
        d.on_client_connected()
        d.on_wake_word_detected()
        assert d.mww == MWWState.STOPPED

    def test_restarts_after_pipeline(self):
        d = Device()
        d.on_client_connected()
        d.on_wake_word_detected()
        d.on_stt_vad_end()
        d.on_tts_response()
        d.on_media_idle()
        assert d.mww == MWWState.RUNNING

    def test_restarts_after_error(self):
        d = Device()
        d.on_client_connected()
        d.on_wake_word_detected()
        d.on_va_error()
        assert d.mww == MWWState.RUNNING

    def test_restarts_after_music_stop(self):
        d = Device()
        d.on_client_connected()
        d.on_play_media()
        d.on_media_stop()
        assert d.mww == MWWState.RUNNING

    def test_no_start_when_muted(self):
        d = Device(mute_switch=True)
        d.on_client_connected()
        assert d.mww == MWWState.STOPPED

    def test_mute_stops_mww(self):
        d = Device()
        d.on_client_connected()
        assert d.mww == MWWState.RUNNING

        d.toggle_mute(True)
        assert d.mww == MWWState.STOPPED

    def test_unmute_starts_mww(self):
        d = Device(mute_switch=True)
        d.toggle_mute(False)
        assert d.mww == MWWState.RUNNING

    def test_no_start_when_ww_disabled(self):
        d = Device(use_wake_word=False)
        d.on_client_connected()
        assert d.mww == MWWState.STOPPED


class TestCenterTouchBehavior:
    """Center touch does different things depending on state"""

    def test_idle_starts_ptt(self):
        d = Device()
        d.center_touch()
        assert d.voice_assistant == VoiceAssistantState.LISTENING

    def test_listening_stops_va(self):
        d = Device(voice_assistant=VoiceAssistantState.LISTENING, mic_capturing=True)
        d.center_touch()
        assert d.voice_assistant == VoiceAssistantState.IDLE
        assert d.mic_capturing is False

    def test_playing_stops_music(self):
        d = Device(media_player=MediaPlayerState.PLAYING)
        d.center_touch()
        assert d.media_player == MediaPlayerState.IDLE

    def test_playing_takes_priority_over_va(self):
        """If music is playing AND VA is somehow running, stop music"""
        d = Device(
            media_player=MediaPlayerState.PLAYING,
            voice_assistant=VoiceAssistantState.LISTENING,
        )
        d.center_touch()
        assert d.media_player == MediaPlayerState.IDLE
        # VA state unchanged by music stop
        assert d.voice_assistant == VoiceAssistantState.LISTENING


class TestTimerTransitions:
    """Timer lifecycle state transitions"""

    def test_timer_start_increments_count(self):
        d = Device()
        d.on_timer_started()
        assert d.active_timer_count == 1

    def test_multiple_timers(self):
        d = Device()
        d.on_timer_started()
        d.on_timer_started()
        assert d.active_timer_count == 2

    def test_timer_finished_activates_alarm(self):
        d = Device()
        d.on_timer_started()
        d.on_timer_finished()
        assert d.timer_alarm_active is True
        assert d.active_timer_count == 0

    def test_timer_cancel_decrements(self):
        d = Device()
        d.on_timer_started()
        d.on_timer_started()
        d.on_timer_cancelled()
        assert d.active_timer_count == 1
        assert d.timer_alarm_active is False

    def test_dismiss_alarm_clears_state(self):
        d = Device()
        d.on_timer_started()
        d.on_timer_finished()
        d.dismiss_alarm()
        assert d.timer_alarm_active is False

    def test_center_touch_dismisses_alarm(self):
        d = Device()
        d.on_timer_started()
        d.on_timer_finished()
        assert d.timer_alarm_active is True
        d.center_touch()
        assert d.timer_alarm_active is False

    def test_center_touch_alarm_priority_over_music(self):
        """Alarm dismiss beats music stop"""
        d = Device()
        d.on_play_media()
        d.on_timer_started()
        d.on_timer_finished()
        d.center_touch()
        assert d.timer_alarm_active is False
        # Music still playing
        assert d.media_player == MediaPlayerState.PLAYING

    def test_full_timer_lifecycle(self):
        d = Device()
        d.on_client_connected()
        d.on_timer_started()
        assert d.active_timer_count == 1
        d.on_timer_finished()
        assert d.timer_alarm_active is True
        d.center_touch()
        assert d.timer_alarm_active is False
        assert d.mww == MWWState.RUNNING


class TestVolumeClick:
    """Volume click conditional behavior"""

    def test_click_plays_when_idle(self):
        d = Device()
        should_click = d.media_player == MediaPlayerState.IDLE
        assert should_click is True

    def test_click_skipped_during_music(self):
        d = Device()
        d.on_play_media()
        should_click = d.media_player == MediaPlayerState.IDLE
        assert should_click is False

    def test_click_skipped_during_tts(self):
        d = Device()
        d.on_client_connected()
        d.on_wake_word_detected()
        d.on_stt_vad_end()
        d.on_tts_response()
        should_click = d.media_player == MediaPlayerState.IDLE
        assert should_click is False

    def test_click_plays_after_music_stops(self):
        d = Device()
        d.on_play_media()
        d.on_media_stop()
        should_click = d.media_player == MediaPlayerState.IDLE
        assert should_click is True
