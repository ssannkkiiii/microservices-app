import uvicorn
from fastapi import FastAPI
from scr import rabbit, ws
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="Translate WebSocket API")

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.on_event("startup")
async def on_startup():
    await rabbit.connect()

@app.on_event("shutdown")
async def on_shutdown():
    await rabbit.disconnect()

ws.register_ws_router(app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
