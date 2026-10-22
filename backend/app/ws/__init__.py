from contextlib import asynccontextmanager
import logging
from uuid import UUID
import asyncio

from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError

from .connection_manager import ConnectionManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

producer = None
consumer = None
connection_manager = ConnectionManager()

async def cancel_and_wait(task):
    task.cancel()
    try:
        return await task
    except asyncio.CancelledError:
        pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    global producer, consumer
    logger.info('lifespan starting')
    
    producer = AIOKafkaProducer(bootstrap_servers='kafka:9092', retry_backoff_ms=1000)  
    consumer = AIOKafkaConsumer(
        'websocket-messages-server',
        bootstrap_servers='kafka:9092',
        retry_backoff_ms=1000)
    
    while True:
        try:
            await producer.start()
            break
        except KafkaConnectionError as e:
            logger.warning(f'connection error, retrying: {e}')
            await asyncio.sleep(1)
    
    while True:
        try:
            await consumer.start()
            break
        except KafkaConnectionError as e:
            logger.warning(f'connection error, retrying: {e}')
            await asyncio.sleep(1)
    
    task = asyncio.create_task(process_server_messages())

    logger.info('lifespan ready')

    yield

    logger.info('lifespan closing')

    await cancel_and_wait(task)
    await producer.stop()
    await consumer.stop()
    producer = None
    consumer = None

    logger.info('lifespan closed')

async def process_server_messages():
    async for msg in consumer:
        logger.info('server msg: {msg}')
        
        connection_id = UUID(bytes=msg.key)
        value = msg.value.decode('utf-8')
        logger.info(f'connection_id={connection_id} value={value}')

        await connection_manager.send_text(connection_id, value)

ws_app = FastAPI(lifespan=lifespan)

@ws_app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    connection_id = await connection_manager.add_connection(websocket)

    try:
        while True:
            text = await websocket.receive_text()

            key = connection_id.bytes
            data = text.encode('utf-8')
            logger.info(f'send message {key} {data}')
            await producer.send('websocket-messages-client', key=key, value=data)
    except WebSocketDisconnect:
        await connection_manager.remove_connection(connection_id)