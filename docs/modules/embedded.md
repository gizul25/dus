Copy `config.cmake.example` to `config.cmake` and fill in with real values.

```bash
cd certs/
set -x MQTT_SERVER ametrine.test
set -x SERVER_CN ametrine.test
set -x CLIENT_CN pico123
./makecerts.sh
```

```bash
# update mosquitto.conf
mosquitto -c mosquitto.conf
set -x MQTT_SERVER ametrine.test
set -x SERVER_CN ametrine.test
# add --insecure if using IP for MQTT_SERVER
mosquitto_sub -h $MQTT_SERVER --cafile certs/$SERVER_CN/ca.crt --key certs/$SERVER_CN/client.key --cert certs/$SERVER_CN/client.crt -t 'test/topic' -v
mosquitto_pub -h $MQTT_SERVER --cafile certs/$SERVER_CN/ca.crt --key certs/$SERVER_CN/client.key --cert certs/$SERVER_CN/client.crt -t 'test/topic' -m 'hello world'
# build project and flash

mosquitto_sub -h $MQTT_SERVER --cafile certs/$SERVER_CN/ca.crt --key certs/$SERVER_CN/client.key --cert certs/$SERVER_CN/client.crt -t 'pico/pico123/sensors' -v --insecure
```

- `mosquitto_sub` verifies server certificate CN to make sure server certificate is valid, which produces a lot of silent and annoying errors on local networks. Using IP addresses is brutal, so you have to use DNS. For example, even for localhost, you have to use `localhost` name instead of 127.0.0.1. Also, domains with `.local` are handled uniquely with mDNS, and I wanted to avoid that and use just DNS. 
- So server cert must have `CN=` field with domain, not IP, and it should be the one used to connect to the server. Else, you'll get server certificate validation errors, which often appear as opaque errors. Adding `--insecure` works as bypass for `mosquitto_sub` for example, if needed, but it's just to verify the issue.
- I have updated code, so MQTT_SERVER can be IP or DNS, and SERVER_CN is always DNS, so it is possible to not run DNS and just provide IP to Pico, but still have certs working. As in, do DNS resolution kinda at compilation time. But this only applies to Pico, and `mosquitto_sub` and `mosquitto_pub` commands are still very picky about hostname.

Testing:
- Hotspot with WIFI_SSID and WIFI_PASSWORD set
- Main DNS server (for laptop hotspot it is laptop itself), make sure that MQTT_SERVER resolves to MQTT server IP address. For me, I update `/etc/resolv.conf` with `nameserver 127.0.0.1`, and then use dnsmasq
`/etc/dnsmasq.conf` for reference:

```ini
no-resolv
no-poll
address=/ametrine.test/192.168.12.1
```

There we so many confusing bland errors, it took 4 hrs to fix up all of the TLS/SSL stuff.

```bash
openssl x509 -in certs/$MQTT_SERVER/client.crt -text -noout
openssl x509 -in <certificate>.crt -text -noout | grep "Version"
openssl verify -CAfile certs/$MQTT_SERVER/ca.crt certs/$MQTT_SERVER/client.crt

openssl s_client -connect localhost:8883
openssl s_client -connect localhost:8883 -CAfile certs/$MQTT_SERVER/ca.crt -key certs/$MQTT_SERVER/client.key -cert certs/$MQTT_SERVER/client.crt
```

Cert validation fails on mosquitto_sub side, which seems to fail to verify server cert. `--insecure` fixes.

For curious ones, here's some relevant resources:
- https://www.nongnu.org/lwip/2_1_x/group__dns.html
- https://www.nongnu.org/lwip/2_0_x/group__mqtt.html
- https://hyring.com/learn/raspberry-pi/light-sensor (that light sensor is relative)
- https://source.coderefinery.org/sdm-edu/phce-2026
- https://github.com/raspberrypi/pico-examples/tree/master/pico_w/wifi/mqtt
- https://mosquitto.org/
- https://github.com/eclipse-mosquitto/mosquitto/tree/master
- https://mosquitto.org/man/mosquitto-conf-5.html