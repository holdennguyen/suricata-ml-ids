"""
Real-time Detector Service for Suricata ML-IDS
Provides real-time threat detection with <100ms latency using ensemble ML models
"""

import asyncio
import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
import json

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
import redis.asyncio as redis
from pydantic import BaseModel

from detector_engine import DetectorEngine
from model_manager import ModelManager
from feature_processor import FeatureProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize components
detector_engine = DetectorEngine()
model_manager = ModelManager()
feature_processor = FeatureProcessor()

# Configuration
MODELS_DIR = Path("/app/models")
LOGS_DIR = Path("/app/logs")
LATENCY_TARGET = int(os.getenv("LATENCY_TARGET_MS", "100"))
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

# Redis connection
redis_client = None

class DetectionRequest(BaseModel):
    features: Dict[str, float]
    timestamp: Optional[float] = None
    source_ip: Optional[str] = None
    dest_ip: Optional[str] = None

class DetectionResponse(BaseModel):
    prediction: str
    confidence: float
    threat_score: float
    model_predictions: Dict[str, Any]
    processing_time_ms: float
    timestamp: float

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        if self.active_connections:
            disconnected = []
            for connection in self.active_connections:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.append(connection)
            
            # Remove disconnected clients
            for conn in disconnected:
                self.disconnect(conn)

websocket_manager = WebSocketManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize service on startup"""
    global redis_client
    
    logger.info("Starting Real-time Detector Service...")
    
    # Create directories
    MODELS_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)
    
    # Initialize Redis connection
    try:
        redis_client = redis.from_url(REDIS_URL)
        await redis_client.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Running without Redis.")
        redis_client = None
    
    # Load available models
    await model_manager.load_models(MODELS_DIR)
    
    # Initialize detector engine
    await detector_engine.initialize(model_manager)
    
    logger.info(f"Real-time Detector Service started with {LATENCY_TARGET}ms latency target")
    yield
    # Cleanup on shutdown
    if redis_client:
        await redis_client.close()
    logger.info("Real-time Detector Service stopped")

# Initialize FastAPI app
app = FastAPI(
    title="Real-time Detector Service",
    description="Real-time network intrusion detection with ensemble ML models",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    models_loaded = len(model_manager.models)
    redis_status = "connected" if redis_client else "disconnected"
    
    return {
        "status": "healthy",
        "service": "realtime-detector",
        "models_loaded": models_loaded,
        "redis_status": redis_status,
        "latency_target_ms": LATENCY_TARGET
    }

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Real-time Detector",
        "version": "1.0.0",
        "description": "Real-time network intrusion detection with ensemble ML models",
        "latency_target_ms": LATENCY_TARGET,
        "models_loaded": len(model_manager.models),
        "endpoints": {
            "health": "/health",
            "detect": "/detect",
            "batch_detect": "/batch-detect",
            "models": "/models",
            "stats": "/stats",
            "websocket": "/ws"
        }
    }

@app.post("/detect", response_model=DetectionResponse)
async def detect_threat(request: DetectionRequest):
    """Detect threats in real-time with <100ms latency"""
    start_time = time.time()
    
    try:
        # Process features
        processed_features = await feature_processor.process_features(request.features)
        
        # Perform detection
        detection_result = await detector_engine.detect(processed_features)
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Create response
        response = DetectionResponse(
            prediction=detection_result["prediction"],
            confidence=detection_result["confidence"],
            threat_score=detection_result["threat_score"],
            model_predictions=detection_result["model_predictions"],
            processing_time_ms=processing_time,
            timestamp=time.time()
        )
        
        # Log high-threat detections
        if detection_result["threat_score"] > 0.7:
            logger.warning(f"High threat detected: {detection_result['prediction']} "
                         f"(confidence: {detection_result['confidence']:.3f})")
        
        # Broadcast to WebSocket clients
        await websocket_manager.broadcast({
            "type": "detection",
            "data": response.dict()
        })
        
        # Cache result in Redis if available
        if redis_client:
            try:
                cache_key = f"detection:{request.source_ip}:{int(time.time())}"
                await redis_client.setex(
                    cache_key, 
                    300,  # 5 minutes TTL
                    json.dumps(response.dict(), default=str)
                )
            except Exception as e:
                logger.debug(f"Redis cache error: {e}")
        
        # Check latency target
        if processing_time > LATENCY_TARGET:
            logger.warning(f"Latency target exceeded: {processing_time:.1f}ms > {LATENCY_TARGET}ms")
        
        return response
        
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        logger.error(f"Error in threat detection: {str(e)} (took {processing_time:.1f}ms)")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch-detect")
async def batch_detect_threats(requests: List[DetectionRequest]):
    """Batch threat detection for multiple samples"""
    start_time = time.time()
    
    try:
        results = []
        
        for request in requests:
            # Process features
            processed_features = await feature_processor.process_features(request.features)
            
            # Perform detection
            detection_result = await detector_engine.detect(processed_features)
            
            results.append({
                "features": request.features,
                "prediction": detection_result["prediction"],
                "confidence": detection_result["confidence"],
                "threat_score": detection_result["threat_score"]
            })
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "results": results,
            "batch_size": len(requests),
            "total_processing_time_ms": processing_time,
            "avg_processing_time_ms": processing_time / len(requests)
        }
        
    except Exception as e:
        logger.error(f"Error in batch detection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def list_models():
    """List loaded models and their information"""
    return {
        "models": model_manager.get_model_info(),
        "total_models": len(model_manager.models)
    }

@app.get("/stats")
async def get_service_stats():
    """Get service performance statistics"""
    try:
        stats = await detector_engine.get_stats()
        
        return {
            "detections_performed": stats.get("detections_performed", 0),
            "avg_processing_time_ms": stats.get("avg_processing_time_ms", 0),
            "threats_detected": stats.get("threats_detected", 0),
            "models_loaded": len(model_manager.models),
            "latency_target_ms": LATENCY_TARGET,
            "active_websocket_connections": len(websocket_manager.active_connections)
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time detection streaming"""
    await websocket_manager.connect(websocket)
    
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_json()
            
            if data.get("type") == "detection_request":
                # Process detection request via WebSocket
                request_data = data.get("data", {})
                
                try:
                    # Create detection request
                    request = DetectionRequest(**request_data)
                    
                    # Perform detection
                    start_time = time.time()
                    processed_features = await feature_processor.process_features(request.features)
                    detection_result = await detector_engine.detect(processed_features)
                    processing_time = (time.time() - start_time) * 1000
                    
                    # Send response back to client
                    response = {
                        "type": "detection_response",
                        "data": {
                            "prediction": detection_result["prediction"],
                            "confidence": detection_result["confidence"],
                            "threat_score": detection_result["threat_score"],
                            "processing_time_ms": processing_time,
                            "timestamp": time.time()
                        }
                    }
                    
                    await websocket.send_json(response)
                    
                except Exception as e:
                    error_response = {
                        "type": "error",
                        "data": {"message": str(e)}
                    }
                    await websocket.send_json(error_response)
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=False,
        log_level="info"
    )
