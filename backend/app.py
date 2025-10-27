"""FastAPI WebSocket server for real-time segmentation."""

import asyncio
import json
import time
from typing import Dict, Optional
from collections import deque

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

from models import ModelLoader, InferenceEngine
from utils import (
    COCO_CLASSES,
    ADE20K_CLASSES,
    SERVER_CONFIG,
    MODEL_PROFILES
)
from utils.frame_processor import FrameProcessor
from utils.segmentation_viz import SegmentationVisualizer


# Initialize FastAPI app
app = FastAPI(title="Real-Time Segmentation Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=SERVER_CONFIG["cors_origins"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend)
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# Global instances
model_loader: Optional[ModelLoader] = None
frame_processor: Optional[FrameProcessor] = None


class ConnectionManager:
    """Manages WebSocket connections and processing state."""

    def __init__(self):
        self.active_connections: Dict[WebSocket, Dict] = {}
        self.frame_queue: Dict[WebSocket, deque] = {}
        self.max_queue_size = SERVER_CONFIG["max_queue_size"]

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()

        # Initialize connection state
        self.active_connections[websocket] = {
            "model_mode": SERVER_CONFIG["default_model"],
            "viz_mode": "filled",
            "opacity": 0.6,
            "class_filter": None,
            "inference_engine": None,
            "visualizer": None
        }

        # Initialize frame queue
        self.frame_queue[websocket] = deque(maxlen=self.max_queue_size)

        print(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            del self.active_connections[websocket]
        if websocket in self.frame_queue:
            del self.frame_queue[websocket]

        print(f"Client disconnected. Total connections: {len(self.active_connections)}")

    def get_state(self, websocket: WebSocket) -> Optional[Dict]:
        """Get state for a specific connection."""
        return self.active_connections.get(websocket)

    def update_state(self, websocket: WebSocket, updates: Dict):
        """Update state for a specific connection."""
        if websocket in self.active_connections:
            self.active_connections[websocket].update(updates)

    def queue_frame(self, websocket: WebSocket, frame_data: str, timestamp: int):
        """Add frame to processing queue."""
        if websocket in self.frame_queue:
            self.frame_queue[websocket].append({
                "data": frame_data,
                "timestamp": timestamp
            })

    def get_next_frame(self, websocket: WebSocket) -> Optional[Dict]:
        """Get next frame from queue."""
        if websocket in self.frame_queue and len(self.frame_queue[websocket]) > 0:
            return self.frame_queue[websocket].popleft()
        return None


# Global connection manager
manager = ConnectionManager()


@app.on_event("startup")
async def startup_event():
    """Initialize models and processors on startup."""
    global model_loader, frame_processor

    print("Initializing server...")

    # Initialize model loader
    model_loader = ModelLoader()

    # Preload default model
    print(f"Loading default model: {SERVER_CONFIG['default_model']}")
    model_loader.load_model(SERVER_CONFIG["default_model"])

    # Initialize frame processor
    frame_processor = FrameProcessor()

    print("Server initialized successfully")


@app.get("/")
async def root():
    """Serve the main frontend page."""
    with open("../frontend/index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "available_models": model_loader.get_available_modes() if model_loader else [],
        "active_connections": len(manager.active_connections)
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time segmentation."""
    await manager.connect(websocket)

    # Initialize inference engine for this connection
    state = manager.get_state(websocket)
    inference_engine = InferenceEngine(model_loader, frame_processor)
    inference_engine.set_model_mode(state["model_mode"])

    # Warm up the model
    inference_engine.warm_up()

    # Get class labels based on model
    config = MODEL_PROFILES[state["model_mode"]]
    class_labels = COCO_CLASSES if config.num_classes == 21 else ADE20K_CLASSES[:30]

    # Initialize visualizer
    visualizer = SegmentationVisualizer(num_classes=config.num_classes)

    # Update state
    manager.update_state(websocket, {
        "inference_engine": inference_engine,
        "visualizer": visualizer
    })

    # Send connection acknowledgement
    await websocket.send_json({
        "type": "connected",
        "status": "ready",
        "available_models": model_loader.get_available_modes(),
        "class_labels": class_labels,
        "current_model": state["model_mode"]
    })

    try:
        while True:
            # Receive message from client
            message = await websocket.receive_text()
            data = json.loads(message)

            msg_type = data.get("type")

            if msg_type == "frame":
                # Queue the frame for processing
                await handle_frame(websocket, data)

            elif msg_type == "change_mode":
                await handle_mode_change(websocket, data)

            elif msg_type == "update_viz":
                await handle_viz_update(websocket, data)

            elif msg_type == "get_stats":
                await handle_stats_request(websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket)
        await websocket.close()


async def handle_frame(websocket: WebSocket, data: Dict):
    """Process a video frame and return segmentation."""
    try:
        state = manager.get_state(websocket)
        if not state:
            return

        inference_engine = state["inference_engine"]
        visualizer = state["visualizer"]

        # Decode frame
        frame_data = data.get("data")
        timestamp = data.get("timestamp", 0)

        frame = frame_processor.decode_frame(frame_data)

        # Run inference
        mask, metadata = inference_engine.predict(frame)

        # Get detected classes
        detected_classes = inference_engine.get_detected_classes(mask)

        # Create visualization
        viz_frame = visualizer.render(
            frame,
            mask,
            mode=state["viz_mode"],
            opacity=state["opacity"],
            class_filter=state["class_filter"]
        )

        # Encode result
        encoded_result = frame_processor.encode_frame(viz_frame, format="jpeg")

        # Get class labels
        config = MODEL_PROFILES[state["model_mode"]]
        class_labels = COCO_CLASSES if config.num_classes == 21 else ADE20K_CLASSES[:30]
        detected_class_names = [class_labels[i] for i in detected_classes if i < len(class_labels)]

        # Send result
        await websocket.send_json({
            "type": "segmentation",
            "timestamp": timestamp,
            "data": encoded_result,
            "metadata": {
                **metadata,
                "detected_classes": detected_class_names
            }
        })

    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "code": "INFERENCE_FAILED",
            "message": str(e),
            "recoverable": True
        })


async def handle_mode_change(websocket: WebSocket, data: Dict):
    """Handle model mode change request."""
    try:
        new_mode = data.get("model_mode")

        if new_mode not in MODEL_PROFILES:
            await websocket.send_json({
                "type": "error",
                "code": "INVALID_MODE",
                "message": f"Invalid model mode: {new_mode}",
                "recoverable": True
            })
            return

        state = manager.get_state(websocket)
        inference_engine = state["inference_engine"]

        # Switch model
        inference_engine.set_model_mode(new_mode)
        inference_engine.warm_up()

        # Update visualizer for new number of classes
        config = MODEL_PROFILES[new_mode]
        visualizer = SegmentationVisualizer(num_classes=config.num_classes)

        # Update state
        manager.update_state(websocket, {
            "model_mode": new_mode,
            "visualizer": visualizer
        })

        # Get new class labels
        class_labels = COCO_CLASSES if config.num_classes == 21 else ADE20K_CLASSES[:30]

        await websocket.send_json({
            "type": "mode_changed",
            "model_mode": new_mode,
            "class_labels": class_labels
        })

    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "code": "MODE_CHANGE_FAILED",
            "message": str(e),
            "recoverable": True
        })


async def handle_viz_update(websocket: WebSocket, data: Dict):
    """Handle visualization settings update."""
    try:
        settings = data.get("settings", {})

        updates = {}
        if "overlay_opacity" in settings:
            updates["opacity"] = settings["overlay_opacity"]
        if "visualization_mode" in settings:
            updates["viz_mode"] = settings["visualization_mode"]
        if "class_filter" in settings:
            updates["class_filter"] = settings["class_filter"]

        manager.update_state(websocket, updates)

        await websocket.send_json({
            "type": "viz_updated",
            "settings": updates
        })

    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "code": "VIZ_UPDATE_FAILED",
            "message": str(e),
            "recoverable": True
        })


async def handle_stats_request(websocket: WebSocket):
    """Handle performance stats request."""
    try:
        state = manager.get_state(websocket)
        inference_engine = state["inference_engine"]

        stats = inference_engine.get_performance_stats()

        await websocket.send_json({
            "type": "stats",
            **stats
        })

    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "code": "STATS_FAILED",
            "message": str(e),
            "recoverable": True
        })


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=SERVER_CONFIG["host"],
        port=SERVER_CONFIG["port"],
        log_level=SERVER_CONFIG["log_level"]
    )
