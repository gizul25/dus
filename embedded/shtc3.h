#ifndef SHTC3_H
#define SHTC3_H

#include <cstdint>

#include "i2c_bus.h"

namespace hw
{
    // The SHTC3 temperature and humidity sensor. It does not make its own bus: it is
    // given one in the constructor.
    class Shtc3
    {
    public:
        static constexpr std::uint8_t ADDRESS {0x70};

        explicit Shtc3(I2cBus& bus);

        // Measures both. Returns false if the bus or the checksum failed.
        bool measure();

        // from the last measure() that worked
        float temperature() const { return temperature_; }  // degrees Celsius
        float humidity() const { return humidity_; }        // percent

    private:
        bool send_command(std::uint16_t command);

        // a reference: Shtc3 uses the bus, it does not own it
        I2cBus& bus_;
        float temperature_ {0.0f};
        float humidity_ {0.0f};
    };
}

#endif  // SHTC3_H
