import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from .mqtt_kafka_bridge import Bridge, SensorReading


cert_path = "app/bridge/certs/dus.test.com"


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    await fast_mqtt.mqtt_startup()
    yield
    await fast_mqtt.mqtt_shutdown()

bridge_app = FastAPI(lifespan=_lifespan)

loop = asyncio.get_event_loop()

bridge = Bridge(cert_path, loop)

fast_mqtt = bridge.mqtt

@fast_mqtt.on_connect()
def connect(client, flags, rc, properties):
    fast_mqtt.client.subscribe("mqtt")  # subscribing mqtt topic
    print("Connected: ", client, flags, rc, properties)


@fast_mqtt.on_message()
async def message(client, topic, payload, qos, properties):
    print("Received message: ", topic, payload.decode(), qos, properties)
    return 0


@fast_mqtt.subscribe("my/mqtt/topic/#")
async def message_to_topic(client, topic, payload, qos, properties):
    print("Received message to specific topic: ", topic, payload.decode(), qos, properties)


@fast_mqtt.on_disconnect()
def disconnect(client, packet, exc=None):
    print("Disconnected")


@fast_mqtt.on_subscribe()
def subscribe(client, mid, qos, properties):
    print("subscribed", client, mid, qos, properties)


@bridge_app.get("/")
async def func():
    fast_mqtt.publish("mqtt", "Hello from Fastapi")  # publishing mqtt topic

    return {"result": True, "message": "Published"}