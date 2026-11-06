#include "sensor_mqtt.h"

#include <iostream>
#include <format>
#include "pico/cyw43_arch.h"

namespace
{
    const uint32_t ASYNC_WORKER_TIME_MS = 5000;
}

SensorMQTT::SensorMQTT(hw::I2cBus& bus)
    : MQTT{MQTT_CLIENT_NAME}, sensor_{bus}
{
    async_worker = {
        .do_work = async_worker_fn,
        .user_data = this
    };
}

void SensorMQTT::on_register_topics(bool sub)
{
    MQTT::on_register_topics(sub);

    // Currently nothing to listen to
}

void SensorMQTT::on_topic()
{
    MQTT::on_topic();

    // Currently nothing to listen to
}

void SensorMQTT::init_workers()
{
    MQTT::init_workers();

    async_context_add_at_time_worker_in_ms(cyw43_arch_async_context(), &async_worker, 0);
}

void SensorMQTT::async_worker_fn(async_context_t *context, async_at_time_worker_t *worker)
{
    SensorMQTT* mqtt = (SensorMQTT*)worker->user_data;
    mqtt->on_async_worker();
    async_context_add_at_time_worker_in_ms(context, worker, ASYNC_WORKER_TIME_MS);
}

void SensorMQTT::on_async_worker()
{
    if (!sensor_.measure()) 
    {
        std::cout << "measure failed" << std::endl;
        return;
    }

    float temperature = sensor_.temperature();
    float humidity = sensor_.humidity();
    float brightness = light_.measure();
    std::cout << "Temperature (in C): " << temperature << ", humidity: " << humidity << std::endl;
    std::cout << "Brightness: " << brightness << std::endl;

    std::string topic = std::format("pico/{}/sensors", MQTT_CLIENT_NAME);
    SensorPacket packet;
    packet.temperature = temperature;
    packet.humidity = humidity;
    packet.brightness = brightness;

    publish(topic.c_str(), &packet, sizeof(packet));
}