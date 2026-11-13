#include <cstdint>
#include <iostream>
#include <pico/stdio.h>

#include "hardware/i2c.h"
#include "pico/cyw43_arch.h"
#include "lwip/dns.h"
#include "i2c_bus.h"
#include "sensor_mqtt.h"

constexpr std::uint32_t SDA_PIN {4};
constexpr std::uint32_t SCL_PIN {5};
constexpr std::uint32_t I2C_BAUDRATE {400'000};  // 400 kHz

const std::uint32_t WIFI_CONNECT_TIMEOUT_MS = 30000;

static void dns_found(const char *hostname, const ip_addr_t *ipaddr, void *arg) {
    if (ipaddr) {
        SensorMQTT* mqtt = (SensorMQTT*) arg;
        mqtt->start_client(*ipaddr);
    } else {
        std::cout << "dns request failed" << std::endl;
    }
}

int main()
{
    stdio_init_all();

    std::cout << "embedded started" << std::endl;

    if (cyw43_arch_init()) {
        std::cout << "Failed to initialize CYW43" << std::endl;
        return 1;
    }

    cyw43_arch_enable_sta_mode();
    if (cyw43_arch_wifi_connect_timeout_ms(WIFI_SSID, WIFI_PASSWORD, CYW43_AUTH_WPA2_AES_PSK, WIFI_CONNECT_TIMEOUT_MS)) {
        std::cout << "Failed to connect to WiFi" << std::endl;
        return 1;
    }
    std::cout << std::endl << "Connected to WiFi" << std::endl;

    hw::I2cBus bus {i2c0, SDA_PIN, SCL_PIN, I2C_BAUDRATE};
    SensorMQTT mqtt{bus};

    // We are not in a callback so locking is needed when calling lwip
    // Make a DNS request for the MQTT server IP address
    cyw43_arch_lwip_begin();
    ip_addr_t ipaddr;
    int err = dns_gethostbyname(MQTT_SERVER, &ipaddr, dns_found, &mqtt);
    cyw43_arch_lwip_end();

    if (err == ERR_OK) {
        // We have the address, just start the client
        dns_found(MQTT_SERVER, &ipaddr, &mqtt);
    } else if (err != ERR_INPROGRESS) { // ERR_INPROGRESS means expect a callback
        std::cout << "DNS request failed" << std::endl;
        return 1;
    }

    // We are not in a callback but we can get away with calling mqtt_client_is_connected()
    // because it's a read-only operation
    mqtt.loop();

    std::cout << "MQTT client exiting" << std::endl;
    cyw43_arch_disable_sta_mode();
    cyw43_arch_deinit();
}