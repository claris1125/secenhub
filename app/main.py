from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Set
import os, json, time

SCENE_TOKEN = os.getenv("SCENE_TOKEN", "changeme")

app = FastAPI(title="SceneHub (Linux)")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Serve static assets (GLB files) from ../assets
ASSETS_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "assets"))
if not os.path.isdir(ASSETS_DIR):
    os.makedirs(ASSETS_DIR, exist_ok=True)
app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

class Obj(BaseModel):
    id: int
    class_name: str = Field(alias="class")
    mesh_uri: str
    position_m: List[float]
    orientation_xyzw: List[float]
    scale: List[float] = [1, 1, 1]

class SceneDiff(BaseModel):
    frame: str = "map"
    timestamp: float = 0.0
    objects: List[Obj]

latest: Dict[str, Any] = {}
ws_set: Set[WebSocket] = set()

def check_token(tok: str):
    if tok != SCENE_TOKEN:
        raise HTTPException(status_code=401, detail="bad token")

@app.post("/api/scene/push")
async def push_scene(diff: SceneDiff, x_scene_token: str = Header(default="")):
    check_token(x_scene_token)
    payload = diff.model_dump(by_alias=True)
    if not payload.get("timestamp"):
        payload["timestamp"] = time.time()
    latest["data"] = payload

    # Broadcast to all connected websockets
    dead = []
    for ws in list(ws_set):
        try:
            await ws.send_text(json.dumps(payload))
        except Exception:
            dead.append(ws)
    for ws in dead:
        try:
            await ws.close()
        except Exception:
            pass
        ws_set.discard(ws)

    return {"ok": True}

@app.get("/api/scene/latest")
async def get_latest():
    return latest.get("data", {"frame": "map", "timestamp": 0, "objects": []})

@app.websocket("/ws/scene")
async def ws_scene(ws: WebSocket):
    await ws.accept()
    ws_set.add(ws)
    try:
        if "data" in latest:
            await ws.send_text(json.dumps(latest["data"]))
        while True:
            await ws.receive_text()  # keepalive
    except WebSocketDisconnect:
        pass
    finally:
        ws_set.discard(ws)
