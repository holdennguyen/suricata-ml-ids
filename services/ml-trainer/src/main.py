"""
ML Trainer Service for Suricata ML-IDS
Trains and evaluates Decision Tree and k-NN models for network intrusion detection
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
import time

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np

from ml_trainer import MLTrainer
from model_evaluator import ModelEvaluator
from data_processor import DataProcessor
from models import TrainingRequest, TrainingResponse, EvaluationResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize components
ml_trainer = MLTrainer()
model_evaluator = ModelEvaluator()
data_processor = DataProcessor()

# Configuration
DATASETS_DIR = Path("/app/datasets")
MODELS_DIR = Path("/app/models")
RESULTS_DIR = Path("/app/results")
ACCURACY_TARGET = float(os.getenv("ML_ACCURACY_TARGET", "0.90"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize service on startup"""
    logger.info("Starting ML Trainer Service...")
    
    # Create directories if they don't exist
    DATASETS_DIR.mkdir(exist_ok=True)
    MODELS_DIR.mkdir(exist_ok=True)
    RESULTS_DIR.mkdir(exist_ok=True)
    
    logger.info(f"ML Trainer Service started with accuracy target: {ACCURACY_TARGET}")
    yield
    # Cleanup on shutdown
    logger.info("ML Trainer Service shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="ML Trainer Service",
    description="Trains and evaluates ML models for network intrusion detection",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ml-trainer"}

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "ML Trainer",
        "version": "1.0.0",
        "description": "Trains and evaluates ML models for network intrusion detection",
        "accuracy_target": ACCURACY_TARGET,
        "supported_algorithms": ["decision_tree", "knn", "ensemble"],
        "endpoints": {
            "health": "/health",
            "train": "/train",
            "evaluate": "/evaluate",
            "models": "/models",
            "datasets": "/datasets",
            "stats": "/stats"
        }
    }

@app.post("/train", response_model=TrainingResponse)
async def train_models(
    request: TrainingRequest,
    background_tasks: BackgroundTasks
):
    """Train ML models on the provided dataset"""
    try:
        start_time = time.time()
        
        # Validate dataset
        dataset_path = DATASETS_DIR / request.dataset_filename
        if not dataset_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Dataset not found: {request.dataset_filename}"
            )
        
        logger.info(f"Starting training with dataset: {dataset_path}")
        
        # Load and preprocess data
        df = pd.read_csv(dataset_path)
        X, y, feature_names = await data_processor.prepare_training_data(
            df, 
            target_column=request.target_column,
            test_size=request.test_size
        )
        
        # Train models
        training_results = {}
        
        if "decision_tree" in request.algorithms:
            dt_result = await ml_trainer.train_decision_tree(
                X, y, feature_names, request.hyperparameters.get("decision_tree", {})
            )
            training_results["decision_tree"] = dt_result
        
        if "knn" in request.algorithms:
            knn_result = await ml_trainer.train_knn(
                X, y, feature_names, request.hyperparameters.get("knn", {})
            )
            training_results["knn"] = knn_result
        
        if "ensemble" in request.algorithms:
            ensemble_result = await ml_trainer.train_ensemble(
                X, y, feature_names, request.hyperparameters.get("ensemble", {})
            )
            training_results["ensemble"] = ensemble_result
        
        # Save models
        model_files = {}
        for algorithm, result in training_results.items():
            model_filename = f"{request.dataset_filename.stem}_{algorithm}_model.joblib"
            model_path = MODELS_DIR / model_filename
            
            await ml_trainer.save_model(result["model"], model_path)
            model_files[algorithm] = model_filename
            
            logger.info(f"Saved {algorithm} model to: {model_path}")
        
        # Calculate overall training time
        training_time = time.time() - start_time
        
        # Find best performing model
        best_algorithm = max(
            training_results.keys(),
            key=lambda k: training_results[k]["accuracy"]
        )
        best_accuracy = training_results[best_algorithm]["accuracy"]
        
        # Check if accuracy target is met
        target_met = best_accuracy >= ACCURACY_TARGET
        
        response = TrainingResponse(
            dataset_filename=request.dataset_filename,
            algorithms_trained=list(training_results.keys()),
            training_results=training_results,
            model_files=model_files,
            best_algorithm=best_algorithm,
            best_accuracy=best_accuracy,
            accuracy_target_met=target_met,
            training_time=training_time
        )
        
        # Save training results
        results_filename = f"{request.dataset_filename.stem}_training_results.json"
        results_path = RESULTS_DIR / results_filename
        
        with open(results_path, 'w') as f:
            import json
            json.dump(response.dict(), f, indent=2, default=str)
        
        logger.info(f"Training completed. Best accuracy: {best_accuracy:.4f} ({best_algorithm})")
        
        return response
        
    except Exception as e:
        logger.error(f"Error training models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_model(
    model_filename: str,
    test_dataset_filename: str,
    background_tasks: BackgroundTasks
):
    """Evaluate a trained model on test data"""
    try:
        # Validate model file
        model_path = MODELS_DIR / model_filename
        if not model_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Model not found: {model_filename}"
            )
        
        # Validate test dataset
        test_dataset_path = DATASETS_DIR / test_dataset_filename
        if not test_dataset_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Test dataset not found: {test_dataset_filename}"
            )
        
        logger.info(f"Evaluating model: {model_filename} on dataset: {test_dataset_filename}")
        
        # Load model and test data
        model = await ml_trainer.load_model(model_path)
        test_df = pd.read_csv(test_dataset_path)
        
        # Prepare test data
        X_test, y_test, _ = await data_processor.prepare_test_data(test_df)
        
        # Evaluate model
        evaluation_results = await model_evaluator.evaluate_model(
            model, X_test, y_test
        )
        
        # Generate detailed report
        report_filename = f"{model_filename.stem}_evaluation_report.json"
        report_path = RESULTS_DIR / report_filename
        
        with open(report_path, 'w') as f:
            import json
            json.dump(evaluation_results, f, indent=2, default=str)
        
        response = EvaluationResponse(
            model_filename=model_filename,
            test_dataset_filename=test_dataset_filename,
            evaluation_results=evaluation_results,
            report_filename=report_filename
        )
        
        logger.info(f"Model evaluation completed. Accuracy: {evaluation_results['accuracy']:.4f}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error evaluating model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def list_models():
    """List all trained models"""
    try:
        model_files = list(MODELS_DIR.glob("*.joblib"))
        
        models_info = []
        for model_path in model_files:
            try:
                stat = model_path.stat()
                models_info.append({
                    "filename": model_path.name,
                    "size_bytes": stat.st_size,
                    "created": stat.st_mtime,
                    "algorithm": model_path.stem.split('_')[-2] if '_' in model_path.stem else "unknown"
                })
            except Exception as e:
                models_info.append({
                    "filename": model_path.name,
                    "error": str(e)
                })
        
        return {"models": models_info}
        
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/datasets")
async def list_datasets():
    """List all available datasets"""
    try:
        dataset_files = list(DATASETS_DIR.glob("*.csv"))
        
        datasets_info = []
        for dataset_path in dataset_files:
            try:
                df = pd.read_csv(dataset_path, nrows=1)  # Read just header
                stat = dataset_path.stat()
                
                datasets_info.append({
                    "filename": dataset_path.name,
                    "size_bytes": stat.st_size,
                    "created": stat.st_mtime,
                    "feature_count": len(df.columns),
                    "sample_count": len(pd.read_csv(dataset_path))
                })
            except Exception as e:
                datasets_info.append({
                    "filename": dataset_path.name,
                    "error": str(e)
                })
        
        return {"datasets": datasets_info}
        
    except Exception as e:
        logger.error(f"Error listing datasets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_service_stats():
    """Get service statistics"""
    try:
        model_files = list(MODELS_DIR.glob("*.joblib"))
        dataset_files = list(DATASETS_DIR.glob("*.csv"))
        result_files = list(RESULTS_DIR.glob("*.json"))
        
        return {
            "models_trained": len(model_files),
            "datasets_available": len(dataset_files),
            "training_results": len(result_files),
            "accuracy_target": ACCURACY_TARGET,
            "service_uptime": "running",
            "supported_algorithms": ["decision_tree", "knn", "ensemble"]
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=False,
        log_level="info"
    )
