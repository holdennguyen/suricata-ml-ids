"""
Feature Extractor Service for Suricata ML-IDS
Extracts 25+ features from PCAP files and Suricata logs for ML training
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import pandas as pd

from feature_engine import FeatureEngine
from pcap_processor import PCAPProcessor
from suricata_log_parser import SuricataLogParser
from models import FeatureExtractionRequest, FeatureExtractionResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Feature Extractor Service",
    description="Extracts network features from PCAP files for ML training",
    version="1.0.0"
)

# Initialize components
feature_engine = FeatureEngine()
pcap_processor = PCAPProcessor()
log_parser = SuricataLogParser()

# Configuration
PCAP_DIR = Path("/app/pcaps")
DATASET_DIR = Path("/app/datasets")
LOGS_DIR = Path("/app/logs")

@app.on_startup
async def startup_event():
    """Initialize service on startup"""
    logger.info("Starting Feature Extractor Service...")
    
    # Create directories if they don't exist
    PCAP_DIR.mkdir(exist_ok=True)
    DATASET_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)
    
    logger.info("Feature Extractor Service started successfully")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "feature-extractor"}

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Feature Extractor",
        "version": "1.0.0",
        "description": "Extracts network features from PCAP files for ML training",
        "endpoints": {
            "health": "/health",
            "extract": "/extract",
            "batch_extract": "/batch-extract",
            "features": "/features",
            "stats": "/stats"
        }
    }

@app.post("/extract", response_model=FeatureExtractionResponse)
async def extract_features(
    request: FeatureExtractionRequest,
    background_tasks: BackgroundTasks
):
    """Extract features from a single PCAP file"""
    try:
        pcap_path = PCAP_DIR / request.pcap_filename
        
        if not pcap_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"PCAP file not found: {request.pcap_filename}"
            )
        
        # Process PCAP file
        logger.info(f"Processing PCAP file: {pcap_path}")
        packets = await pcap_processor.process_pcap(pcap_path)
        
        # Extract features
        features = await feature_engine.extract_features(packets)
        
        # Save features to CSV
        output_filename = f"{request.pcap_filename.stem}_features.csv"
        output_path = DATASET_DIR / output_filename
        
        df = pd.DataFrame([features])
        df.to_csv(output_path, index=False)
        
        logger.info(f"Features extracted and saved to: {output_path}")
        
        return FeatureExtractionResponse(
            pcap_filename=request.pcap_filename,
            output_filename=output_filename,
            feature_count=len(features),
            features=features
        )
        
    except Exception as e:
        logger.error(f"Error extracting features: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch-extract")
async def batch_extract_features(background_tasks: BackgroundTasks):
    """Extract features from all PCAP files in the directory"""
    try:
        pcap_files = list(PCAP_DIR.glob("*.pcap")) + list(PCAP_DIR.glob("*.pcapng"))
        
        if not pcap_files:
            raise HTTPException(
                status_code=404,
                detail="No PCAP files found in the directory"
            )
        
        results = []
        for pcap_file in pcap_files:
            try:
                # Process each PCAP file
                logger.info(f"Processing PCAP file: {pcap_file}")
                packets = await pcap_processor.process_pcap(pcap_file)
                
                # Extract features
                features = await feature_engine.extract_features(packets)
                
                # Save features to CSV
                output_filename = f"{pcap_file.stem}_features.csv"
                output_path = DATASET_DIR / output_filename
                
                df = pd.DataFrame([features])
                df.to_csv(output_path, index=False)
                
                results.append({
                    "pcap_filename": pcap_file.name,
                    "output_filename": output_filename,
                    "feature_count": len(features),
                    "status": "success"
                })
                
            except Exception as e:
                logger.error(f"Error processing {pcap_file}: {str(e)}")
                results.append({
                    "pcap_filename": pcap_file.name,
                    "error": str(e),
                    "status": "failed"
                })
        
        return {"results": results, "total_processed": len(pcap_files)}
        
    except Exception as e:
        logger.error(f"Error in batch extraction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/features")
async def list_feature_files():
    """List all available feature files"""
    try:
        feature_files = list(DATASET_DIR.glob("*_features.csv"))
        
        files_info = []
        for file_path in feature_files:
            try:
                df = pd.read_csv(file_path)
                files_info.append({
                    "filename": file_path.name,
                    "feature_count": len(df.columns),
                    "sample_count": len(df),
                    "created": file_path.stat().st_mtime
                })
            except Exception as e:
                files_info.append({
                    "filename": file_path.name,
                    "error": str(e)
                })
        
        return {"feature_files": files_info}
        
    except Exception as e:
        logger.error(f"Error listing feature files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_service_stats():
    """Get service statistics"""
    try:
        pcap_files = list(PCAP_DIR.glob("*.pcap")) + list(PCAP_DIR.glob("*.pcapng"))
        feature_files = list(DATASET_DIR.glob("*_features.csv"))
        
        return {
            "pcap_files_available": len(pcap_files),
            "feature_files_generated": len(feature_files),
            "service_uptime": "running",
            "supported_features": feature_engine.get_feature_names()
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )
