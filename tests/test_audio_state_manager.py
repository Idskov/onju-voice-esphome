"""
AudioStateManager Model Tests

Models the new C++ AudioStateManager component's behavior:
- State transitions with priority-based preemption
- Preemption stack (push/pop)
- LED state mapping
- Error/disconnect handling

Run with: pytest tests/test_audio_state_manager.py -v
"""

from dataclasses import dataclass, field
from enum import IntEnum
from typing import List, Optional
import pytest


class AudioState(IntEnum):
    """Matches C++ AudioState enum. Higher value = higher priority."""
    STANDBY = 0
    LISTENING = 1
    PROCESSING = 2
    RESPONDING = 3
    MUSIC = 4
    ANNOUNCING = 5
    ALERTING = 6


class LedEffect(IntEnum):
    """Expected LED effect per state."""
    OFF = 0
    LISTENING_WW = 1
    LISTENING = 2
    PROCESSING = 3
    SPEAKING = 4
    MUSIC_PULSE = 5
    ALARM_FLASH = 6


# Preemption priority (separate from enum value).
# MUSIC has lower *priority* (1) than LISTENING (2), so wake word CAN preempt music.
# This is intentional: voice interaction takes precedence over passive playback.
PREEMPTION_PRIORITY = {
    AudioState.STANDBY: 0,
    AudioState.MUSIC: 1,
    AudioState.LISTENING: 2,
    AudioState.PROCESSING: 3,
    AudioState.RESPONDING: 4,
    AudioState.ANNOUNCING: 5,
    AudioState.ALERTING: 6,
}

LED_MAP = {
    AudioState.STANDBY: LedEffect.LISTENING_WW,
    AudioState.LISTENING: LedEffect.LISTENING,
    AudioState.PROCESSING: LedEffect.PROCESSING,
    AudioState.RESPONDING: LedEffect.SPEAKING,
    AudioState.MUSIC: LedEffect.MUSIC_PULSE,
    AudioState.ANNOUNCING: LedEffect.SPEAKING,
    AudioState.ALERTING: LedEffect.ALARM_FLASH,
}


@dataclass
class AudioStateManager:
    """Python model of the C++ AudioStateManager component."""
    current_state: AudioState = AudioState.STANDBY
    stack: List[AudioState] = field(default_factory=list)
    log: List[str] = field(default_factory=list)
    enter_count: dict = field(default_factory=lambda: {s: 0 for s in AudioState})
    exit_count: dict = field(default_factory=lambda: {s: 0 for s in AudioState})

    def _priority(self, state: AudioState) -> int:
        return PREEMPTION_PRIORITY[state]

    def request_state(self, new_state: AudioState) -> bool:
        """Request a state transition. Returns True if transition occurred."""
        if new_state == self.current_state:
            self.log.append(f"NOOP: already in {new_state.name}")
            return False

        new_prio = self._priority(new_state)
        cur_prio = self._priority(self.current_state)

        if new_prio > cur_prio:
            self.log.append(f"PREEMPT: {self.current_state.name} -> {new_state.name} (push {self.current_state.name})")
            self.exit_count[self.current_state] += 1
            self.stack.append(self.current_state)
            self.current_state = new_state
            self.enter_count[new_state] += 1
            return True
        else:
            self.log.append(f"REJECT: {new_state.name} (prio {new_prio} <= current {self.current_state.name} prio {cur_prio})")
            return False

    def pop_state(self) -> AudioState:
        """Pop the preemption stack, resuming the previous state."""
        if not self.stack:
            self.log.append(f"POP: stack empty, going to STANDBY")
            self.exit_count[self.current_state] += 1
            self.current_state = AudioState.STANDBY
            self.enter_count[AudioState.STANDBY] += 1
            return AudioState.STANDBY

        prev = self.stack.pop()
        self.log.append(f"POP: {self.current_state.name} -> {prev.name} (resume)")
        self.exit_count[self.current_state] += 1
        self.current_state = prev
        self.enter_count[prev] += 1
        return prev

    def force_standby(self):
        """Force reset to STANDBY, clearing entire stack (error/disconnect)."""
        self.log.append(f"FORCE_STANDBY: from {self.current_state.name}, clearing stack of {len(self.stack)} items")
        self.exit_count[self.current_state] += 1
        self.stack.clear()
        self.current_state = AudioState.STANDBY
        self.enter_count[AudioState.STANDBY] += 1

    @property
    def led_effect(self) -> LedEffect:
        return LED_MAP[self.current_state]

    @property
    def stack_depth(self) -> int:
        return len(self.stack)


# --- Tests ---

class TestBasicTransitions:
    """Test the transition table from the spec."""

    def test_standby_to_listening(self):
        asm = AudioStateManager()
        assert asm.current_state == AudioState.STANDBY
        assert asm.request_state(AudioState.LISTENING)
        assert asm.current_state == AudioState.LISTENING

    def test_listening_to_processing(self):
        asm = AudioStateManager()
        asm.request_state(AudioState.LISTENING)
        assert asm.request_state(AudioState.PROCESSING)
        assert asm.current_state == AudioState.PROCESSING

    def test_processing_to_responding(self):
        asm = AudioStateManager()
        asm.request_state(AudioState.LISTENING)
        asm.request_state(AudioState.PROCESSING)
        assert asm.request_state(AudioState.RESPONDING)
        assert asm.current_state == AudioState.RESPONDING

    def test_responding_pops_to_processing(self):
        """TTS done -> pop -> PROCESSING (top of stack)."""
        asm = AudioStateManager()
        asm.request_state(AudioState.LISTENING)
        asm.request_state(AudioState.PROCESSING)
        asm.request_state(AudioState.RESPONDING)
        result = asm.pop_state()
        assert result == AudioState.PROCESSING
        asm.pop_state()
        assert asm.current_state == AudioState.LISTENING

    def test_standby_to_alerting(self):
        asm = AudioStateManager()
        assert asm.request_state(AudioState.ALERTING)
        assert asm.current_state == AudioState.ALERTING
        assert asm.stack == [AudioState.STANDBY]

    def test_standby_to_music(self):
        asm = AudioStateManager()
        assert asm.request_state(AudioState.MUSIC)
        assert asm.current_state == AudioState.MUSIC
        assert asm.stack == [AudioState.STANDBY]

    def test_noop_same_state(self):
        asm = AudioStateManager()
        assert not asm.request_state(AudioState.STANDBY)
        assert asm.current_state == AudioState.STANDBY


class TestFullVoiceAssistFlow:
    """Test: STANDBY -> LISTENING -> PROCESSING -> RESPONDING -> STANDBY"""

    def test_full_va_flow(self):
        asm = AudioStateManager()
        asm.request_state(AudioState.LISTENING)
        assert asm.current_state == AudioState.LISTENING
        asm.request_state(AudioState.PROCESSING)
        assert asm.current_state == AudioState.PROCESSING
        asm.request_state(AudioState.RESPONDING)
        assert asm.current_state == AudioState.RESPONDING
        asm.pop_state()  # -> PROCESSING
        asm.pop_state()  # -> LISTENING
        asm.pop_state()  # -> STANDBY
        assert asm.current_state == AudioState.STANDBY
        assert asm.stack_depth == 0

    def test_listening_timeout_to_standby(self):
        """Timeout during LISTENING -> pop back to STANDBY."""
        asm = AudioStateManager()
        asm.request_state(AudioState.LISTENING)
        asm.pop_state()
        assert asm.current_state == AudioState.STANDBY


class TestAlarmPreemption:
    """Test alarm preemption and resumption."""

    def test_alarm_preempts_standby(self):
        asm = AudioStateManager()
        asm.request_state(AudioState.ALERTING)
        assert asm.current_state == AudioState.ALERTING
        assert asm.stack == [AudioState.STANDBY]
        asm.pop_state()
        assert asm.current_state == AudioState.STANDBY

    def test_alarm_preempts_music(self):
        asm = AudioStateManager()
        asm.request_state(AudioState.MUSIC)
        asm.request_state(AudioState.ALERTING)
        assert asm.current_state == AudioState.ALERTING
        assert AudioState.MUSIC in asm.stack
        asm.pop_state()
        assert asm.current_state == AudioState.MUSIC

    def test_alarm_preempts_responding(self):
        asm = AudioStateManager()
        asm.request_state(AudioState.LISTENING)
        asm.request_state(AudioState.PROCESSING)
        asm.request_state(AudioState.RESPONDING)
        asm.request_state(AudioState.ALERTING)
        assert asm.current_state == AudioState.ALERTING
        asm.pop_state()
        assert asm.current_state == AudioState.RESPONDING

    def test_alarm_preempts_announcing(self):
        asm = AudioStateManager()
        asm.request_state(AudioState.MUSIC)
        asm.request_state(AudioState.ANNOUNCING)
        asm.request_state(AudioState.ALERTING)
        assert asm.current_state == AudioState.ALERTING
        asm.pop_state()
        assert asm.current_state == AudioState.ANNOUNCING
        asm.pop_state()
        assert asm.current_state == AudioState.MUSIC


class TestMusicPreemption:
    """Test music state with voice assist and announcements."""

    def test_announcing_preempts_music(self):
        asm = AudioStateManager()
        asm.request_state(AudioState.MUSIC)
        asm.request_state(AudioState.ANNOUNCING)
        assert asm.current_state == AudioState.ANNOUNCING
        assert AudioState.MUSIC in asm.stack
        asm.pop_state()
        assert asm.current_state == AudioState.MUSIC

    def test_music_stops_to_standby(self):
        """Sendspin disconnect -> force to STANDBY."""
        asm = AudioStateManager()
        asm.request_state(AudioState.MUSIC)
        asm.force_standby()
        assert asm.current_state == AudioState.STANDBY
        assert asm.stack_depth == 0

    def test_listening_preempts_music(self):
        """LISTENING (prio 2) > MUSIC (prio 1) -> preempts."""
        asm = AudioStateManager()
        asm.request_state(AudioState.MUSIC)
        result = asm.request_state(AudioState.LISTENING)
        assert result is True
        assert asm.current_state == AudioState.LISTENING
        assert AudioState.MUSIC in asm.stack


class TestNestedPreemption:
    """Test deeply nested preemption stacks."""

    def test_music_announce_alarm_unwind(self):
        """MUSIC -> ANNOUNCING -> ALERTING -> dismiss -> ANNOUNCING -> done -> MUSIC"""
        asm = AudioStateManager()
        asm.request_state(AudioState.MUSIC)
        asm.request_state(AudioState.ANNOUNCING)
        asm.request_state(AudioState.ALERTING)
        assert asm.stack == [AudioState.STANDBY, AudioState.MUSIC, AudioState.ANNOUNCING]
        asm.pop_state()
        assert asm.current_state == AudioState.ANNOUNCING
        asm.pop_state()
        assert asm.current_state == AudioState.MUSIC
        asm.pop_state()
        assert asm.current_state == AudioState.STANDBY

    def test_stack_depth_limit(self):
        """Stack should never exceed 6 (one per non-current state)."""
        asm = AudioStateManager()
        asm.request_state(AudioState.MUSIC)
        asm.request_state(AudioState.LISTENING)
        asm.request_state(AudioState.PROCESSING)
        asm.request_state(AudioState.RESPONDING)
        asm.request_state(AudioState.ANNOUNCING)
        asm.request_state(AudioState.ALERTING)
        assert asm.stack_depth <= 6


class TestPriorityRejection:
    """Test that lower-priority requests are rejected."""

    def test_music_rejected_during_alerting(self):
        asm = AudioStateManager()
        asm.request_state(AudioState.ALERTING)
        assert not asm.request_state(AudioState.MUSIC)
        assert asm.current_state == AudioState.ALERTING

    def test_standby_rejected_during_responding(self):
        asm = AudioStateManager()
        asm.request_state(AudioState.LISTENING)
        asm.request_state(AudioState.PROCESSING)
        asm.request_state(AudioState.RESPONDING)
        assert not asm.request_state(AudioState.STANDBY)
        assert asm.current_state == AudioState.RESPONDING

    def test_music_rejected_during_listening(self):
        asm = AudioStateManager()
        asm.request_state(AudioState.LISTENING)
        assert not asm.request_state(AudioState.MUSIC)
        assert asm.current_state == AudioState.LISTENING


class TestForceStandby:
    """Test error/disconnect force reset."""

    def test_force_clears_stack(self):
        asm = AudioStateManager()
        asm.request_state(AudioState.MUSIC)
        asm.request_state(AudioState.ANNOUNCING)
        asm.request_state(AudioState.ALERTING)
        asm.force_standby()
        assert asm.current_state == AudioState.STANDBY
        assert asm.stack_depth == 0

    def test_force_from_any_state(self):
        for state in AudioState:
            if state == AudioState.STANDBY:
                continue
            asm = AudioStateManager()
            asm.request_state(state)
            asm.force_standby()
            assert asm.current_state == AudioState.STANDBY


class TestLedMapping:
    """Test LED effect for each state."""

    def test_all_states_have_led(self):
        for state in AudioState:
            asm = AudioStateManager()
            if state != AudioState.STANDBY:
                asm.current_state = state
            assert asm.led_effect == LED_MAP[state]

    def test_standby_led(self):
        asm = AudioStateManager()
        assert asm.led_effect == LedEffect.LISTENING_WW

    def test_alerting_led(self):
        asm = AudioStateManager()
        asm.current_state = AudioState.ALERTING
        assert asm.led_effect == LedEffect.ALARM_FLASH


class TestLedPriorityIntegration:
    """Verify LED effects match the spec's priority order during transitions."""

    def test_va_flow_led_sequence(self):
        asm = AudioStateManager()
        assert asm.led_effect == LedEffect.LISTENING_WW
        asm.request_state(AudioState.LISTENING)
        assert asm.led_effect == LedEffect.LISTENING
        asm.request_state(AudioState.PROCESSING)
        assert asm.led_effect == LedEffect.PROCESSING
        asm.request_state(AudioState.RESPONDING)
        assert asm.led_effect == LedEffect.SPEAKING
        asm.pop_state()
        assert asm.led_effect == LedEffect.PROCESSING
        asm.pop_state()
        assert asm.led_effect == LedEffect.LISTENING
        asm.pop_state()
        assert asm.led_effect == LedEffect.LISTENING_WW

    def test_alarm_during_music_led(self):
        asm = AudioStateManager()
        asm.request_state(AudioState.MUSIC)
        assert asm.led_effect == LedEffect.MUSIC_PULSE
        asm.request_state(AudioState.ALERTING)
        assert asm.led_effect == LedEffect.ALARM_FLASH
        asm.pop_state()
        assert asm.led_effect == LedEffect.MUSIC_PULSE
