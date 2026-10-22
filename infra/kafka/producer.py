from aiokafka import AIOKafkaProducer
import asyncio
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

async def send_one():
    session = PromptSession()
    producer = AIOKafkaProducer(bootstrap_servers='kafka:9092')
    await producer.start()

    key = b'4567'
    while True:
        with patch_stdout():
            text = await session.prompt_async("Say something: ")
        data = text.encode('utf-8')

        await producer.send_and_wait("websocket-messages", key=key, value=data)

    await producer.stop()

asyncio.run(send_one())