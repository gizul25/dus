#include "mqtt.h"

#include <cstdint>
#include <string>
#include <iostream>
#include "lwip/altcp_tls.h"
#include "lwip/apps/mqtt.h"
#include "lwip/apps/mqtt_priv.h" // needed to set hostname
#include "pico/cyw43_arch.h"

#ifdef MQTT_CERT_INC
#include MQTT_CERT_INC
#endif

namespace
{
    const std::uint8_t MQTT_SUBSCRIBE_QOS = 1;
    const std::uint8_t MQTT_PUBLISH_QOS = 1;
    const std::uint8_t MQTT_PUBLISH_RETAIN = 0;

    const std::uint16_t MQTT_KEEP_ALIVE_S = 60;
    const std::string MQTT_WILL_TOPIC = "/online";
    const char* MQTT_WILL_MSG = "0";
    const std::uint8_t MQTT_WILL_QOS = 1;
}

MQTT::MQTT(const char* client_id)
{
    mqtt_client_info_.client_id = client_id;
    mqtt_client_info_.keep_alive = MQTT_KEEP_ALIVE_S;
    mqtt_client_info_.client_user = NULL;
    mqtt_client_info_.client_pass = NULL;

    mqtt_client_info_.will_topic = MQTT_WILL_TOPIC.c_str();
    mqtt_client_info_.will_msg = MQTT_WILL_MSG;
    mqtt_client_info_.will_qos = MQTT_WILL_QOS;
    mqtt_client_info_.will_retain = true;

    static const uint8_t ca_cert[] = TLS_ROOT_CERT;
    static const uint8_t client_key[] = TLS_CLIENT_KEY;
    static const uint8_t client_cert[] = TLS_CLIENT_CERT;
    mqtt_client_info_.tls_config = altcp_tls_create_config_client_2wayauth(
        ca_cert, sizeof(ca_cert),
        client_key, sizeof(client_key),
        NULL, 0,
        client_cert, sizeof(client_cert)
    );
}

void MQTT::start_client(ip_addr_t mqtt_server_address)
{
    const int port = MQTT_TLS_PORT;

    cyw43_arch_lwip_begin();
    mqtt_client_inst_ = mqtt_client_new();
    cyw43_arch_lwip_end();
    if (!mqtt_client_inst_) {
        std::cout << "MQTT client instance creation error" << std::endl;
        return;
    }
    std::cout << "IP address of this device " << ipaddr_ntoa(&(netif_list->ip_addr)) << std::endl;
    std::cout << "Connecting to mqtt server at " << ipaddr_ntoa(&mqtt_server_address) << std::endl;

    cyw43_arch_lwip_begin();
    int res = mqtt_client_connect(mqtt_client_inst_, &mqtt_server_address, port, mqtt_connection_cb, this, &mqtt_client_info_);
    if (res != ERR_OK) {
        std::cout << "MQTT broker connection error: " << res << std::endl;
        return;
    }
#if LWIP_ALTCP && LWIP_ALTCP_TLS
    // This is important for MBEDTLS_SSL_SERVER_NAME_INDICATION
    mbedtls_ssl_set_hostname((struct mbedtls_ssl_context*)altcp_tls_context(mqtt_client_inst_->conn), SERVER_CN);
#endif
    mqtt_set_inpub_callback(mqtt_client_inst_, mqtt_incoming_publish_cb, mqtt_incoming_data_cb, this);
    cyw43_arch_lwip_end();
}

void MQTT::loop()
{
    while (!connect_done_ || mqtt_client_is_connected(mqtt_client_inst_)) {

    #ifdef PICO_CYW43_ARCH_POLL 
        // if you use cyw43_arch in lwip_poll mode then you must periodically call
        // cyw43_arch_poll() from your main loop (see SDK network API documentaion)
        cyw43_arch_poll();
        cyw43_arch_wait_for_work_until(make_timeout_time_ms(10000));
    #else
        // as supplied the example configures cyw43_arch for thread_safe_background
        // operation (see CMakeLists.txt) so there's no need to poll
        sleep_ms(10000);
    #endif

    }
}

void MQTT::mqtt_connection_cb(mqtt_client_t *client, void *arg, mqtt_connection_status_t status)
{
    MQTT* this_ = (MQTT*)arg;
    this_->on_mqtt_connection(client, status);
}

void MQTT::on_mqtt_connection(mqtt_client_t *client, mqtt_connection_status_t status)
{
    if (status == MQTT_CONNECT_ACCEPTED) {
        connect_done_ = true;
        sub_unsub_topics(true);

        // indicate online
        if (mqtt_client_info_.will_topic) {
            mqtt_publish(mqtt_client_inst_, mqtt_client_info_.will_topic, "1", 1, MQTT_WILL_QOS, true, pub_request_cb, this);
        }

        init_workers();
    } else if (status == MQTT_CONNECT_DISCONNECTED) {
        if (!connect_done_) {
            std::cout << "Failed to connect to mqtt server" << std::endl;
        } else {
            std::cout << "Disconnected from mqtt server" << std::endl;
        }
    }
    else {
        std::cout << "Unexpected status: " << status << std::endl;
    }
}

void MQTT::pub_request_cb(__unused void *arg, err_t err)
{
    if (err != 0) {
        std::cout << "pub_request_cb failed " << err << std::endl;
    }
}

void MQTT::register_topic(bool sub, const char* topic)
{
    mqtt_request_cb_t cb = sub ? sub_request_cb : unsub_request_cb;
    mqtt_sub_unsub(mqtt_client_inst_, topic, MQTT_SUBSCRIBE_QOS, cb, this, sub);
}

void MQTT::publish(const char* topic, void* payload, u16_t payload_len)
{
    mqtt_publish(mqtt_client_inst_, topic, payload, payload_len, MQTT_PUBLISH_QOS, MQTT_PUBLISH_RETAIN, pub_request_cb, this);
}

void MQTT::sub_unsub_topics(bool sub)
{
    on_register_topics(sub);
}

void MQTT::on_register_topics(bool sub)
{
    register_topic(sub, "/print");
    register_topic(sub, "/ping");
    register_topic(sub, "/exit");
}

void MQTT::sub_request_cb(void *arg, err_t err)
{
    MQTT* this_ = (MQTT*)arg;
    this_->on_mqtt_sub_request(err);
}

void MQTT::on_mqtt_sub_request(err_t err)
{
    if (err != 0) {
        std::cout << "subscribe request failed " << err << std::endl;
    }
    subscribe_count_++;
}

void MQTT::unsub_request_cb(void *arg, err_t err)
{
    MQTT* this_ = (MQTT*)arg;
    this_->on_mqtt_unsub_request(err);
}

void MQTT::on_mqtt_unsub_request(err_t err)
{
    if (err != 0) {
        std::cout << "unsubscribe request failed " << err << std::endl;
    }
    subscribe_count_--;
    assert(subscribe_count_ >= 0);

    // Stop if requested
    if (subscribe_count_ <= 0 && stop_client_) {
        mqtt_disconnect(mqtt_client_inst_);
    }
}

void MQTT::mqtt_incoming_publish_cb(void *arg, const char *topic, u32_t tot_len)
{
    MQTT* this_ = (MQTT*)arg;
    this_->on_mqtt_incoming_publish(topic, tot_len);
}

void MQTT::on_mqtt_incoming_publish(const char *topic, u32_t tot_len)
{
    // using strlcpy() ensures the string is properly terminated if truncated
    strlcpy(topic_, topic, sizeof(topic_));
}

void MQTT::mqtt_incoming_data_cb(void *arg, const u8_t *data, u16_t len, u8_t flags)
{
    MQTT* this_ = (MQTT*)arg;
    this_->on_mqtt_incoming_data(data, len, flags);
}

void MQTT::on_mqtt_incoming_data(const u8_t *data, u16_t len, u8_t flags)
{
    strncpy(data_, (const char *)data, len);
    len_ = len;
    data_[len_] = '\0';

    std::cout << "Topic: " << topic_ << ", Message: " << data_ << std::endl;
    on_topic();
}

void MQTT::on_topic()
{
    if (strcmp(topic_, "/print") == 0) {
        printf("%.*s\n", len_, data_);
    } else if (strcmp(topic_, "/ping") == 0) {
        char buf[11];
        snprintf(buf, sizeof(buf), "%u", to_ms_since_boot(get_absolute_time()) / 1000);
        mqtt_publish(mqtt_client_inst_, "/uptime", buf, strlen(buf), MQTT_PUBLISH_QOS, MQTT_PUBLISH_RETAIN, pub_request_cb, this);
    } else if (strcmp(topic_, "/exit") == 0) {
        stop_client_ = true; // stop the client when ALL subscriptions are stopped
        sub_unsub_topics(false);
    }
}