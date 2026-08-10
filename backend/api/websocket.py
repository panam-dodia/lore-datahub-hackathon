from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from api.job_store import job_queues

router = APIRouter()


@router.websocket("/ws/excavation/{job_id}")
async def excavation_websocket(websocket: WebSocket, job_id: str):
    """Streams real-time progress messages to the frontend as the
    orchestrator works through an excavation job. Sends `None` is never
    forwarded to the client — it's the internal sentinel that closes the
    socket once the job reaches DONE/FAILED.
    """
    await websocket.accept()

    queue = job_queues.get(job_id)
    if queue is None:
        await websocket.send_json({"error": f"Unknown job_id: {job_id}"})
        await websocket.close()
        return

    try:
        while True:
            message = await queue.get()
            if message is None:
                break
            await websocket.send_json({"message": message})
    except WebSocketDisconnect:
        pass
    finally:
        # The client may have already disconnected (e.g. navigated away
        # mid-excavation) by the time we get here — closing an already-closed
        # socket raises RuntimeError, so only close if it's still open.
        if websocket.application_state != WebSocketState.DISCONNECTED:
            await websocket.close()
