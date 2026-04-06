#include "audio_state_manager.h"
#include "esphome/core/log.h"

namespace esphome {
namespace audio_state_manager {

static const char *TAG = "audio_state_manager";

void AudioStateManager::setup() {
  ESP_LOGCONFIG(TAG, "Setting up AudioStateManager...");
  this->publish_state_();
  this->fire_enter_triggers_(AudioState::STANDBY);
}

void AudioStateManager::dump_config() {
  ESP_LOGCONFIG(TAG, "AudioStateManager:");
  ESP_LOGCONFIG(TAG, "  Current state: %s", audio_state_to_string(this->current_state_));
}

bool AudioStateManager::request_state(AudioState new_state) {
  if (new_state == this->current_state_) {
    ESP_LOGD(TAG, "Already in %s, ignoring request", audio_state_to_string(new_state));
    return false;
  }

  uint8_t new_prio = get_priority(new_state);
  uint8_t cur_prio = get_priority(this->current_state_);

  if (new_prio > cur_prio) {
    ESP_LOGI(TAG, "Preempt: %s -> %s (pushing %s onto stack, depth %d)",
             audio_state_to_string(this->current_state_),
             audio_state_to_string(new_state),
             audio_state_to_string(this->current_state_),
             this->stack_.size());
    this->fire_exit_triggers_(this->current_state_);
    this->stack_.push_back(this->current_state_);
    this->current_state_ = new_state;
    this->publish_state_();
    this->fire_enter_triggers_(new_state);
    return true;
  } else {
    ESP_LOGD(TAG, "Rejected: %s (prio %d) <= current %s (prio %d)",
             audio_state_to_string(new_state), new_prio,
             audio_state_to_string(this->current_state_), cur_prio);
    return false;
  }
}

AudioState AudioStateManager::pop_state() {
  this->fire_exit_triggers_(this->current_state_);

  if (this->stack_.empty()) {
    ESP_LOGW(TAG, "Pop: stack empty, returning to STANDBY");
    this->current_state_ = AudioState::STANDBY;
  } else {
    AudioState prev = this->stack_.back();
    this->stack_.pop_back();
    ESP_LOGI(TAG, "Pop: %s -> %s (resume, stack depth %d)",
             audio_state_to_string(this->current_state_),
             audio_state_to_string(prev),
             this->stack_.size());
    this->current_state_ = prev;
  }

  this->publish_state_();
  this->fire_enter_triggers_(this->current_state_);
  return this->current_state_;
}

void AudioStateManager::force_standby() {
  ESP_LOGW(TAG, "Force STANDBY from %s, clearing stack of %d items",
           audio_state_to_string(this->current_state_),
           this->stack_.size());
  this->fire_exit_triggers_(this->current_state_);
  this->stack_.clear();
  this->current_state_ = AudioState::STANDBY;
  this->publish_state_();
  this->fire_enter_triggers_(AudioState::STANDBY);
}

void AudioStateManager::publish_state_() {
  if (this->status_sensor_ != nullptr) {
    this->status_sensor_->publish_state(audio_state_to_string(this->current_state_));
  }
}

void AudioStateManager::fire_enter_triggers_(AudioState state) {
  std::vector<Trigger<> *> *triggers = nullptr;
  switch (state) {
    case AudioState::STANDBY:    triggers = &this->on_enter_standby_triggers_; break;
    case AudioState::LISTENING:  triggers = &this->on_enter_listening_triggers_; break;
    case AudioState::PROCESSING: triggers = &this->on_enter_processing_triggers_; break;
    case AudioState::RESPONDING: triggers = &this->on_enter_responding_triggers_; break;
    case AudioState::MUSIC:      triggers = &this->on_enter_music_triggers_; break;
    case AudioState::ANNOUNCING: triggers = &this->on_enter_announcing_triggers_; break;
    case AudioState::ALERTING:   triggers = &this->on_enter_alerting_triggers_; break;
  }
  if (triggers != nullptr) {
    for (auto *trigger : *triggers) {
      trigger->trigger();
    }
  }
}

void AudioStateManager::fire_exit_triggers_(AudioState state) {
  std::vector<Trigger<> *> *triggers = nullptr;
  switch (state) {
    case AudioState::STANDBY:    triggers = &this->on_exit_standby_triggers_; break;
    case AudioState::LISTENING:  triggers = &this->on_exit_listening_triggers_; break;
    case AudioState::PROCESSING: triggers = &this->on_exit_processing_triggers_; break;
    case AudioState::RESPONDING: triggers = &this->on_exit_responding_triggers_; break;
    case AudioState::MUSIC:      triggers = &this->on_exit_music_triggers_; break;
    case AudioState::ANNOUNCING: triggers = &this->on_exit_announcing_triggers_; break;
    case AudioState::ALERTING:   triggers = &this->on_exit_alerting_triggers_; break;
  }
  if (triggers != nullptr) {
    for (auto *trigger : *triggers) {
      trigger->trigger();
    }
  }
}

}  // namespace audio_state_manager
}  // namespace esphome
