#include "shtc3.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <hardware/timer.h>

#include "pico/stdlib.h"

namespace
{
    // commands, from the SHTC3 datasheet
    constexpr std::uint16_t WAKE_UP {0x3517};
    constexpr std::uint16_t SLEEP {0xB098};
    constexpr std::uint16_t MEASURE {0x7866};  // temperature first, no clock stretching

    constexpr std::uint32_t WAKE_UP_US {240};
    constexpr std::uint32_t MEASURE_MS {13};  // a measurement takes up to 12.1 ms

    constexpr std::size_t COMMAND_BYTES {2};
    constexpr std::uint32_t BITS_PER_BYTE {8};
    constexpr std::uint16_t LOW_BYTE_MASK {0xFF};

    // the result: temperature (2 bytes, checksum), then humidity (2 bytes, checksum)
    constexpr std::size_t RESULT_BYTES {6};
    constexpr std::size_t TEMPERATURE_HIGH {0};
    constexpr std::size_t TEMPERATURE_LOW {1};
    constexpr std::size_t TEMPERATURE_CRC {2};
    constexpr std::size_t HUMIDITY_HIGH {3};
    constexpr std::size_t HUMIDITY_LOW {4};
    constexpr std::size_t HUMIDITY_CRC {5};
    constexpr std::size_t VALUE_BYTES {2};

    // datasheet: T = -45 + 175 * raw / 65536, RH = 100 * raw / 65536
    constexpr float FULL_SCALE {65536.0f};
    constexpr float TEMPERATURE_OFFSET {-45.0f};
    constexpr float TEMPERATURE_SPAN {175.0f};
    constexpr float HUMIDITY_SPAN {100.0f};

    // checksum: CRC-8, polynomial 0x31, starting at 0xFF
    constexpr std::uint8_t CRC_START {0xFF};
    constexpr std::uint8_t CRC_POLYNOMIAL {0x31};
    constexpr std::uint8_t CRC_TOP_BIT {0x80};

    // The checksum the SHTC3 sends after each 2-byte value.
    std::uint8_t crc8(const std::uint8_t* data, std::size_t length)
    {
        std::uint8_t crc {CRC_START};
        for (std::size_t i {0}; i < length; ++i)
        {
            crc ^= data[i];
            for (unsigned bit {0}; bit < BITS_PER_BYTE; ++bit)
            {
                const bool top {(crc & CRC_TOP_BIT) != 0};
                crc = static_cast<std::uint8_t>(crc << 1);
                if (top)
                {
                    crc ^= CRC_POLYNOMIAL;
                }
            }
        }
        return crc;
    }

    // Joins two bytes into one 16-bit value, high byte first.
    std::uint16_t to_word(std::uint8_t high, std::uint8_t low)
    {
        return static_cast<std::uint16_t>((high << BITS_PER_BYTE) | low);
    }
}

hw::Shtc3::Shtc3(I2cBus& bus) : bus_ {bus}
{
    // the SHTC3 starts asleep and does not answer a scan until it is woken
    send_command(WAKE_UP);
    sleep_us(WAKE_UP_US);
}

bool hw::Shtc3::send_command(std::uint16_t command)
{
    // two bytes, high byte first
    const std::array<std::uint8_t, COMMAND_BYTES> bytes {
        static_cast<std::uint8_t>(command >> BITS_PER_BYTE),
        static_cast<std::uint8_t>(command & LOW_BYTE_MASK)};
    return bus_.write(ADDRESS, bytes.data(), bytes.size());
}

bool hw::Shtc3::measure()
{
    // the SHTC3 sleeps between measurements
    if (!send_command(WAKE_UP))
    {
        return false;
    }
    // Called from async context, normal sleep causes issues
    busy_wait_us(WAKE_UP_US);

    if (!send_command(MEASURE))
    {
        return false;
    }
    busy_wait_ms(MEASURE_MS);

    std::array<std::uint8_t, RESULT_BYTES> result {};
    if (!bus_.read(ADDRESS, result.data(), result.size()))
    {
        return false;
    }

    send_command(SLEEP);

    if (crc8(&result[TEMPERATURE_HIGH], VALUE_BYTES) != result[TEMPERATURE_CRC] ||
        crc8(&result[HUMIDITY_HIGH], VALUE_BYTES) != result[HUMIDITY_CRC])
    {
        return false;
    }

    const std::uint16_t raw_temperature {
        to_word(result[TEMPERATURE_HIGH], result[TEMPERATURE_LOW])};
    const std::uint16_t raw_humidity {to_word(result[HUMIDITY_HIGH], result[HUMIDITY_LOW])};

    temperature_ = -45 + 175 * raw_temperature / FULL_SCALE;
    humidity_ = 100 * raw_humidity / FULL_SCALE;
    return true;
}
