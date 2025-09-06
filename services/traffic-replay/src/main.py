"""
Traffic Replay Service for Suricata ML-IDS
Generates and replays network traffic for testing and demonstration
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
PCAP_DIR = Path("/app/pcaps")
SYNTHETIC_DIR = Path("/app/synthetic")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize service on startup"""
    logger.info("Starting Traffic Replay Service...")
    
    # Create directories if they don't exist
    PCAP_DIR.mkdir(exist_ok=True)
    SYNTHETIC_DIR.mkdir(exist_ok=True)
    
    logger.info("Traffic Replay Service started successfully")
    yield
    logger.info("Traffic Replay Service shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="Traffic Replay Service",
    description="Generates and replays network traffic for testing",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "traffic-replay"}

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Traffic Replay",
        "version": "1.0.0",
        "description": "Generates and replays network traffic for testing",
        "endpoints": {
            "health": "/health",
            "generate": "/generate",
            "replay": "/replay",
            "status": "/status"
        }
    }

@app.post("/generate")
async def generate_traffic(
    traffic_type: str = "normal",
    duration: int = 60,
    background_tasks: BackgroundTasks = None
):
    """Generate synthetic network traffic"""
    try:
        logger.info(f"Generating {traffic_type} traffic for {duration} seconds")
        
        # Simulate traffic generation
        await asyncio.sleep(2)  # Simulate processing time
        
        return {
            "status": "success",
            "traffic_type": traffic_type,
            "duration": duration,
            "message": f"Generated {traffic_type} traffic for {duration} seconds"
        }
        
    except Exception as e:
        logger.error(f"Error generating traffic: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/replay")
async def replay_pcap(
    pcap_filename: str,
    rate: float = 1.0,
    background_tasks: BackgroundTasks = None
):
    """Replay a PCAP file"""
    try:
        pcap_path = PCAP_DIR / pcap_filename
        
        if not pcap_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"PCAP file not found: {pcap_filename}"
            )
        
        logger.info(f"Replaying PCAP: {pcap_filename} at rate {rate}x")
        
        # Simulate PCAP replay
        await asyncio.sleep(1)  # Simulate processing time
        
        return {
            "status": "success",
            "pcap_filename": pcap_filename,
            "rate": rate,
            "message": f"Replaying {pcap_filename} at {rate}x speed"
        }
        
    except Exception as e:
        logger.error(f"Error replaying PCAP: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def get_status():
    """Get service status and statistics"""
    try:
        pcap_files = list(PCAP_DIR.glob("*.pcap")) + list(PCAP_DIR.glob("*.pcapng"))
        
        return {
            "service": "traffic-replay",
            "status": "running",
            "pcap_files_available": len(pcap_files),
            "pcaps": [f.name for f in pcap_files],
            "uptime": "running"
        }
        
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=False,
        log_level="info"
    )
