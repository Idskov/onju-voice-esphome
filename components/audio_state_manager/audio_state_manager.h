#pragma once

#include <vector>
#include "esphome/core/component.h"
#include "esphome/core/automation.h"
#include "esphome/components/text_sensor/text_sensor.h"

namespace esphome {
namespace audio_state_manager {

enum class AudioState : uint8_t {
  STANDBY = 0,
  LISTENING = 1,
  PROCESSING = 2,
  RESPONDING = 3,
  MUSIC = 4,
  ANNOUNCING = 5,
  ALERTING = 6,
};

// Priority for preemption decisions (higher = can preempt lower)
// Different from enum value: MUSIC(prio 1) < LISTENING(prio 2)
static constexpr uint8_t STATE_PRIORITY[] = {
    0,  // STANDBY
    2,  // LISTENING
    3,  // PROCESSING
    4,  // RESPONDING
    1,  // MUSIC
    5,  // ANNOUNCING
    6,  // ALERTING
};

inline uint8_t get_priority(AudioState state) {
  return STATE_PRIORITY[static_cast<uint8_t>(state)];
}

inline const char *audio_state_to_string(AudioState state) {
  switch (state) {
    case AudioState::STANDBY:    return "STANDBY";
    case AudioState::LISTENING:  return "LISTENING";
    case AudioState::PROCESSING: return "PROCESSING";
    case AudioState::RESPONDING: return "RESPONDING";
    case AudioState::MUSIC:      return "MUSIC";
    case AudioState::ANNOUNCING: return "ANNOUNCING";
    case AudioState::ALERTING:   return "ALERTING";
    default:                     return "UNKNOWN";
  }
}

class AudioStateManager : public Component {
 public:
  void setup() override;
  void dump_config() override;
  float get_setup_priority() const override { return setup_priority::LATE; }

  bool request_state(AudioState new_state);
  AudioState pop_state();
  void force_standby();

  AudioState get_current_state() const { return this->current_state_; }
  size_t get_stack_depth() const { return this->stack_.size(); }

  void set_status_sensor(text_sensor::TextSensor *sensor) { this->status_sensor_ = sensor; }

  void add_on_enter_standby_callback(Trigger<> *trigger) { this->on_enter_standby_triggers_.push_back(trigger); }
  void add_on_exit_standby_callback(Trigger<> *trigger) { this->on_exit_standby_triggers_.push_back(trigger); }
  void add_on_enter_listening_callback(Trigger<> *trigger) { this->on_enter_listening_triggers_.push_back(trigger); }
  void add_on_exit_listening_callback(Trigger<> *trigger) { this->on_exit_listening_triggers_.push_back(trigger); }
  void add_on_enter_processing_callback(Trigger<> *trigger) { this->on_enter_processing_triggers_.push_back(trigger); }
  void add_on_exit_processing_callback(Trigger<> *trigger) { this->on_exit_processing_triggers_.push_back(trigger); }
  void add_on_enter_responding_callback(Trigger<> *trigger) { this->on_enter_responding_triggers_.push_back(trigger); }
  void add_on_exit_responding_callback(Trigger<> *trigger) { this->on_exit_responding_triggers_.push_back(trigger); }
  void add_on_enter_music_callback(Trigger<> *trigger) { this->on_enter_music_triggers_.push_back(trigger); }
  void add_on_exit_music_callback(Trigger<> *trigger) { this->on_exit_music_triggers_.push_back(trigger); }
  void add_on_enter_announcing_callback(Trigger<> *trigger) { this->on_enter_announcing_triggers_.push_back(trigger); }
  void add_on_exit_announcing_callback(Trigger<> *trigger) { this->on_exit_announcing_triggers_.push_back(trigger); }
  void add_on_enter_alerting_callback(Trigger<> *trigger) { this->on_enter_alerting_triggers_.push_back(trigger); }
  void add_on_exit_alerting_callback(Trigger<> *trigger) { this->on_exit_alerting_triggers_.push_back(trigger); }

 protected:
  void fire_enter_triggers_(AudioState state);
  void fire_exit_triggers_(AudioState state);
  void publish_state_();

  AudioState current_state_{AudioState::STANDBY};
  std::vector<AudioState> stack_;
  text_sensor::TextSensor *status_sensor_{nullptr};

  std::vector<Trigger<> *> on_enter_standby_triggers_;
  std::vector<Trigger<> *> on_exit_standby_triggers_;
  std::vector<Trigger<> *> on_enter_listening_triggers_;
  std::vector<Trigger<> *> on_exit_listening_triggers_;
  std::vector<Trigger<> *> on_enter_processing_triggers_;
  std::vector<Trigger<> *> on_exit_processing_triggers_;
  std::vector<Trigger<> *> on_enter_responding_triggers_;
  std::vector<Trigger<> *> on_exit_responding_triggers_;
  std::vector<Trigger<> *> on_enter_music_triggers_;
  std::vector<Trigger<> *> on_exit_music_triggers_;
  std::vector<Trigger<> *> on_enter_announcing_triggers_;
  std::vector<Trigger<> *> on_exit_announcing_triggers_;
  std::vector<Trigger<> *> on_enter_alerting_triggers_;
  std::vector<Trigger<> *> on_exit_alerting_triggers_;
};

// --- Trigger classes ---

#define DEFINE_STATE_TRIGGER(NAME, STATE, ENTER_OR_EXIT) \
  class NAME : public Trigger<> { \
   public: \
    explicit NAME(AudioStateManager *parent) { \
      parent->add_##ENTER_OR_EXIT##_##STATE##_callback(this); \
    } \
  };

DEFINE_STATE_TRIGGER(OnEnterStandbyTrigger, standby, on_enter)
DEFINE_STATE_TRIGGER(OnExitStandbyTrigger, standby, on_exit)
DEFINE_STATE_TRIGGER(OnEnterListeningTrigger, listening, on_enter)
DEFINE_STATE_TRIGGER(OnExitListeningTrigger, listening, on_exit)
DEFINE_STATE_TRIGGER(OnEnterProcessingTrigger, processing, on_enter)
DEFINE_STATE_TRIGGER(OnExitProcessingTrigger, processing, on_exit)
DEFINE_STATE_TRIGGER(OnEnterRespondingTrigger, responding, on_enter)
DEFINE_STATE_TRIGGER(OnExitRespondingTrigger, responding, on_exit)
DEFINE_STATE_TRIGGER(OnEnterMusicTrigger, music, on_enter)
DEFINE_STATE_TRIGGER(OnExitMusicTrigger, music, on_exit)
DEFINE_STATE_TRIGGER(OnEnterAnnouncingTrigger, announcing, on_enter)
DEFINE_STATE_TRIGGER(OnExitAnnouncingTrigger, announcing, on_exit)
DEFINE_STATE_TRIGGER(OnEnterAlertingTrigger, alerting, on_enter)
DEFINE_STATE_TRIGGER(OnExitAlertingTrigger, alerting, on_exit)

#undef DEFINE_STATE_TRIGGER

// --- Actions ---

template<typename... Ts>
class RequestStateAction : public Action<Ts...> {
 public:
  RequestStateAction(AudioStateManager *parent) : parent_(parent) {}
  void set_state(uint8_t state) { this->state_ = static_cast<AudioState>(state); }
  void play(const Ts &...x) override { this->parent_->request_state(this->state_); }

 protected:
  AudioStateManager *parent_;
  AudioState state_;
};

template<typename... Ts>
class PopStateAction : public Action<Ts...> {
 public:
  PopStateAction(AudioStateManager *parent) : parent_(parent) {}
  void play(const Ts &...x) override { this->parent_->pop_state(); }

 protected:
  AudioStateManager *parent_;
};

template<typename... Ts>
class ForceStandbyAction : public Action<Ts...> {
 public:
  ForceStandbyAction(AudioStateManager *parent) : parent_(parent) {}
  void play(const Ts &...x) override { this->parent_->force_standby(); }

 protected:
  AudioStateManager *parent_;
};

}  // namespace audio_state_manager
}  // namespace esphome
