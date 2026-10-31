from aiokafka import AIOKafkaConsumer
import asyncio

async def consume():
    consumer = AIOKafkaConsumer(
        'websocket-messages',
        bootstrap_servers='kafka:9092')
    
    await consumer.start()
    try:
        async for msg in consumer:
            print(msg)
            
            key = msg.key.decode('utf-8')
            value = msg.value.decode('utf-8')
            print(f'key={key} value={value}')
    finally:
        await consumer.stop()

asyncio.run(consume())