#ifndef MQTT_H
#define MQTT_H

#include "lwip/apps/mqtt.h"

namespace
{
    const size_t MQTT_TOPIC_LEN = 100;
}

class MQTT
{
public:
    explicit MQTT(const char* client_id);
    void start_client(ip_addr_t mqtt_server_address);
    void loop();
protected:
    virtual void on_register_topics(bool sub);
    virtual void on_topic();
    virtual void init_workers() {};
    void register_topic(bool sub, const char* topic);
    void publish(const char* topic, void* payload, u16_t payload_len);

    char topic_[MQTT_TOPIC_LEN];
    char data_[MQTT_OUTPUT_RINGBUF_SIZE];
    uint32_t len_{0};
private:
    void on_mqtt_connection(mqtt_client_t *client, mqtt_connection_status_t status);
    void on_mqtt_incoming_publish(const char *topic, u32_t tot_len);
    void on_mqtt_incoming_data(const u8_t *data, u16_t len, u8_t flags);
    void on_mqtt_sub_request(err_t err);
    void on_mqtt_unsub_request(err_t err);
    void sub_unsub_topics(bool sub);

    static void mqtt_connection_cb(mqtt_client_t *client, void *arg, mqtt_connection_status_t status);
    static void mqtt_incoming_publish_cb(void *arg, const char *topic, u32_t tot_len);
    static void mqtt_incoming_data_cb(void *arg, const u8_t *data, u16_t len, u8_t flags);
    static void pub_request_cb(__unused void *arg, err_t err);
    static void sub_request_cb(void *arg, err_t err);
    static void unsub_request_cb(void *arg, err_t err);

    mqtt_client_t* mqtt_client_inst_{nullptr};
    struct mqtt_connect_client_info_t mqtt_client_info_;
    bool connect_done_{false};
    int subscribe_count_{0};
    bool stop_client_{false};
};

#endif  // MQTT_H