#ifndef SENSOR_MQTT_H
#define SENSOR_MQTT_H

#include <pico/async_context.h>
#include "mqtt.h"
#include "shtc3.h"
#include "light.h"

struct SensorPacket
{
    float temperature;
    float humidity;
    float brightness;
};

class SensorMQTT : public MQTT
{
public:
    explicit SensorMQTT(hw::I2cBus& bus);
private:
    void on_register_topics(bool sub) override;
    void on_topic() override;
    void init_workers() override;

    void on_async_worker();

    static void async_worker_fn(async_context_t *context, async_at_time_worker_t *worker);

    hw::Shtc3 sensor_;
    hw::Light light_{};
    async_at_time_worker_t async_worker;
};

#endif  // SENSOR_MQTT_H