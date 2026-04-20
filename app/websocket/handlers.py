import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.websocket.manager import websocket_manager

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time data streaming.
    Clients connect to this endpoint to receive live OCR data updates.
    """
    await websocket_manager.connect(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            logger.debug(f"Received message from client: {message}")
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        logger.info("Client disconnected from WebSocket")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket)
