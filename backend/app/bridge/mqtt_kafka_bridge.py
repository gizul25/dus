import ssl
import os

from os import path
from ssl import SSLContext
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from fastapi_mqtt.config import MQTTConfig 
from fastapi_mqtt.fastmqtt import FastMQTT
from pydantic import BaseModel, ValidationError


class Bridge:
    def __init__(self, certpath, loop):

        self.ssl_context = SSLContext(ssl.PROTOCOL_TLSv1_2)
        self.ssl_context.load_cert_chain(certfile=path.relpath(path.join(certpath, 'client.crt')),
                                         keyfile=path.relpath(path.join(certpath, 'client.key')))
        self.ssl_context.check_hostname = False

        self.mqtt_config = MQTTConfig(
            host=os.environ["MQTT_SERVER"],
            port=8883,
            ssl=self.ssl_context,
            keepalive=300,
        )
        
        self.mqtt = FastMQTT(config=self.mqtt_config)
    
        kafka_bootstrap_servers = os.environ["KAFKA_BOOTSTRAP_SERVERS"]
        kafka_topics = ('1', '2')
        kafka_producer = AIOKafkaProducer(bootstrap_servers=kafka_bootstrap_servers)
        kafka_consumer = AIOKafkaConsumer(
            kafka_topics, 
            loop=loop,
            bootstrap_servers=kafka_bootstrap_servers,
        ) 

class SensorReading(BaseModel):
    temperature: float
    humidity: float
    brightness: float

        



        
