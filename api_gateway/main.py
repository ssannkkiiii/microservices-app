import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import websockets
import os

app = FastAPI(title="API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Railway backend URL
# Використовуємо internal domain для підключення між сервісами на Railway
# Якщо це не працює, використайте public domain: wss://microservices-app-production.up.railway.app/ws
BACKEND_WS_URL = os.getenv("BACKEND_WS_URL", "ws://microservices-app.railway.internal:8000/ws")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "api-gateway"}

@app.websocket("/ws")
async def websocket_gateway(websocket: WebSocket):
    await websocket.accept()
    print(f"✅ Gateway: Client connected, forwarding to {BACKEND_WS_URL}")
    
    try:
        async with websockets.connect(BACKEND_WS_URL) as backend_ws:
            print(f"✅ Gateway: Connected to backend at {BACKEND_WS_URL}")
            
            async def forward_to_backend():
                try:
                    while True:
                        data = await websocket.receive_text()
                        await backend_ws.send(data)
                        print(f"📤 Gateway → Backend: {data[:80]}...")
                except WebSocketDisconnect:
                    print("Gateway: Client disconnected (to backend)")
                except Exception as e:
                    print(f"Gateway error (to backend): {e}")
                    raise
            
            async def forward_to_client():
                try:
                    while True:
                        data = await backend_ws.recv()
                        await websocket.send_text(data)
                        print(f"📥 Gateway ← Backend: {data[:80]}...")
                except websockets.exceptions.ConnectionClosed:
                    print("Gateway: Backend connection closed")
                    raise
                except Exception as e:
                    print(f"Gateway error (to client): {e}")
                    raise
            
            try:
                await asyncio.gather(
                    forward_to_backend(),
                    forward_to_client(),
                    return_exceptions=True
                )
            except Exception as e:
                print(f"Gateway gather error: {e}")
            
    except WebSocketDisconnect:
        print("Gateway: Client disconnected")
    except Exception as e:
        print(f"Gateway connection error: {e}")
        try:
            await websocket.close(code=1011, reason=str(e))
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

