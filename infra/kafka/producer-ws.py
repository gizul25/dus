from aiokafka import AIOKafkaProducer
import asyncio
from uuid import UUID
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

async def send_one():
    session = PromptSession()
    producer = AIOKafkaProducer(bootstrap_servers='kafka:9092')
    await producer.start()

    with patch_stdout():
        uuid_text = await session.prompt_async("Connection UUID: ")
    uuid = UUID(uuid_text)

    key = uuid.bytes
    while True:
        with patch_stdout():
            text = await session.prompt_async("Say something: ")
        data = text.encode('utf-8')

        await producer.send_and_wait("websocket-messages-server", key=key, value=data)

    await producer.stop()

asyncio.run(send_one())