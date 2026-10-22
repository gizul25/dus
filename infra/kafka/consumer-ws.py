from aiokafka import AIOKafkaConsumer
from uuid import UUID
import asyncio

async def consume():
    consumer = AIOKafkaConsumer(
        'websocket-messages-client',
        bootstrap_servers='kafka:9092')
    
    await consumer.start()
    try:
        async for msg in consumer:
            print(msg)
            
            key = UUID(bytes=msg.key)
            value = msg.value.decode('utf-8')
            print(f'key={key} value={value}')
    finally:
        await consumer.stop()

asyncio.run(consume())