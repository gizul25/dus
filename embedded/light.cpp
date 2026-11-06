#include "light.h"

#include <cstdint>
#include "hardware/adc.h"

hw::Light::Light()
{
    adc_init();
    adc_gpio_init(Light::LIGHT_PIN);
    adc_select_input(Light::LIGHT_ADC_INPUT);
}

float hw::Light::measure()
{
    const std::uint16_t raw {adc_read()};
    return 1.0f - raw / 4096.0f;
}
