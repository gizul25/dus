#pragma once

#include <cstdint>

namespace height_control {

enum class Position {
    Unknown,
    Sitting,
    Standing,
};

struct Config {
    float seated_max_height_cm = 75.0F;
    float standing_min_height_cm = 95.0F;
    std::uint64_t confirmation_ms = 5000;
};

class HeightControl {
public:
    explicit HeightControl(Config config = {});

    Position update(float height_cm, std::uint64_t timestamp_ms);
    Position position() const noexcept;

private:
    Position classify(float height_cm) const noexcept;
    void clear_pending() noexcept;

    Config config_;
    Position position_ = Position::Unknown;
    Position pending_position_ = Position::Unknown;
    std::uint64_t pending_since_ms_ = 0;
    std::uint64_t last_update_ms_ = 0;
    bool has_update_ = false;
};

}
