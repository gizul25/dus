#include "height_control.hpp"

#include <cmath>
#include <stdexcept>

namespace height_control {

HeightControl::HeightControl(Config config) : config_(config) {
    if (!std::isfinite(config_.seated_max_height_cm) ||
        !std::isfinite(config_.standing_min_height_cm) ||
        config_.seated_max_height_cm <= 0.0F ||
        config_.standing_min_height_cm > 200.0F ||
        config_.seated_max_height_cm >= config_.standing_min_height_cm ||
        config_.confirmation_ms > 300000) {
        throw std::invalid_argument("invalid height control configuration");
    }
}

Position HeightControl::update(float height_cm, std::uint64_t timestamp_ms) {
    if (!std::isfinite(height_cm) || height_cm <= 0.0F || height_cm > 200.0F) {
        throw std::invalid_argument("height must be greater than 0 and at most 200 cm");
    }
    if (has_update_ && timestamp_ms < last_update_ms_) {
        throw std::invalid_argument("timestamp cannot precede the previous update");
    }

    has_update_ = true;
    last_update_ms_ = timestamp_ms;
    const Position candidate = classify(height_cm);

    if (candidate == Position::Unknown || candidate == position_) {
        clear_pending();
        return position_;
    }

    if (position_ == Position::Unknown || config_.confirmation_ms == 0) {
        position_ = candidate;
        clear_pending();
        return position_;
    }

    if (pending_position_ != candidate) {
        pending_position_ = candidate;
        pending_since_ms_ = timestamp_ms;
        return position_;
    }

    if (timestamp_ms - pending_since_ms_ >= config_.confirmation_ms) {
        position_ = candidate;
        clear_pending();
    }

    return position_;
}

Position HeightControl::position() const noexcept {
    return position_;
}

Position HeightControl::classify(float height_cm) const noexcept {
    if (height_cm <= config_.seated_max_height_cm) {
        return Position::Sitting;
    }
    if (height_cm >= config_.standing_min_height_cm) {
        return Position::Standing;
    }
    return Position::Unknown;
}

void HeightControl::clear_pending() noexcept {
    pending_position_ = Position::Unknown;
    pending_since_ms_ = 0;
}

}
