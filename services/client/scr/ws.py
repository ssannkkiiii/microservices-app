import json
import uuid
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from .rabbit import get_channel, publish_request
from .schemas import TranslateRequest
from typing import Callable
import aio_pika

def register_ws_router(app: FastAPI):
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        try:
            channel = get_channel()
        except Exception as e:
            await websocket.close(code=1011)
            return
        
        reply_queue = await channel.declare_queue(exclusive=True, auto_delete=True)
        print(f"🔔 Created reply queue: {reply_queue.name} for websocket client")

        stop_event = asyncio.Event()

        async def reply_consumer():
            try:
                async with reply_queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        async with message.process():
                            try:
                                body = message.body.decode()
                                data = json.loads(body)
                                await websocket.send_text(json.dumps(data))
                            except Exception as ex:
                                print("Error handling reply message:", ex)
                        if stop_event.is_set():
                            break
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print("reply_consumer error:", e)

        consumer_task = asyncio.create_task(reply_consumer())

        try:
            while True:
                msg = await websocket.receive_text()
                payload = json.loads(msg)
                req = TranslateRequest(**payload)
                request_id = str(uuid.uuid4())
                req.request_id = request_id

                await publish_request(
                    body_bytes=json.dumps(req.dict()).encode(),
                    routing_key="translate_requests",
                    correlation_id=request_id,
                    reply_to=reply_queue.name,
                )
                print("📤 Sent request:", request_id)
        except WebSocketDisconnect:
            print("WebSocket disconnected")
        except Exception as e:
            print("WebSocket error:", e)
        finally:
            stop_event.set()
            consumer_task.cancel()
            try:
                await reply_queue.delete()
            except Exception:
                pass
    