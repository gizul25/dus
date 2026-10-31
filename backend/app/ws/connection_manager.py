import asyncio
import logging
import uuid

logger = logging.getLogger(__name__)

class ConnectionManager:
    websockets = {}
    lock = asyncio.Lock()

    async def add_connection(self, websocket):
        connection_id = uuid.uuid4()
        async with self.lock:
            self.websockets[connection_id] = websocket
        logger.info(f'new connection: {connection_id}')
        return connection_id
    
    async def remove_connection(self, connection_id):
        async with self.lock:
            del self.websockets[connection_id]
        logger.info(f'remove connection: {connection_id}')
    
    async def send_text(self, connection_id, value):
        async with self.lock:
            if not connection_id in self.websockets:
                logger.warning(f'websocket connection_id not found: {connection_id}')
                return
        
            websocket = self.websockets[connection_id]
            await websocket.send_text(value)