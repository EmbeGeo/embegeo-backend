from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.websocket.manager import websocket_manager

router = APIRouter()


@router.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time data streaming.
    Clients connect to this endpoint to receive live OCR data updates.
    """
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive, await for messages (though none expected from client in this case)
            # This can be used to handle incoming messages from clients if needed
            message = await websocket.receive_text()
            print(
                f"Received message from client: {message}"
            )  # For debugging, can be removed
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        print(f"Client disconnected from WebSocket.")
    except Exception as e:
        print(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket)
