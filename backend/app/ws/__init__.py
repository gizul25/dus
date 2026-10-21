from fastapi import Depends, FastAPI, WebSocket
import logging

logger = logging.getLogger(__name__)

ws_app = FastAPI()

@ws_app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    logger.info('in the call')
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")