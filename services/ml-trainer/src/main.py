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

@app.post("/train")
async def train_models(request: TrainingRequest):
    """Train ML models on the provided dataset"""
    try:
        start_time = time.time()
        logger.info(f"Starting training with dataset: {DATASETS_DIR / request.dataset_filename}")
        
        # Validate dataset
        dataset_path = DATASETS_DIR / request.dataset_filename
        if not dataset_path.exists():
            # Check for NSL-KDD datasets and download if needed
            if request.dataset_filename in ['nsl_kdd_sample.csv', 'nsl_kdd_processed.csv']:
                logger.info(f"NSL-KDD dataset {request.dataset_filename} not found, downloading...")
                await download_nsl_kdd_dataset()
                if not dataset_path.exists():
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to download NSL-KDD dataset: {request.dataset_filename}"
                    )
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Dataset not found: {request.dataset_filename}"
                )
        
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
            logger.info("Training Decision Tree...")
            dt_result = await ml_trainer.train_decision_tree(
                X, y, feature_names, request.hyperparameters.get("decision_tree", {})
            )
            training_results["decision_tree"] = dt_result
            logger.info(f"Decision Tree training completed: {dt_result['accuracy']:.4f} accuracy")
        
        if "knn" in request.algorithms:
            logger.info("Training k-NN...")
            knn_result = await ml_trainer.train_knn(
                X, y, feature_names, request.hyperparameters.get("knn", {})
            )
            training_results["knn"] = knn_result
            logger.info(f"k-NN training completed: {knn_result['accuracy']:.4f} accuracy")
        
        if "ensemble" in request.algorithms:
            logger.info("Training Ensemble...")
            ensemble_result = await ml_trainer.train_ensemble(
                X, y, feature_names, request.hyperparameters.get("ensemble", {})
            )
            training_results["ensemble"] = ensemble_result
            logger.info(f"Ensemble training completed: {ensemble_result['accuracy']:.4f} accuracy")
        
        # Save models and create response
        model_files = {}
        dataset_stem = Path(request.dataset_filename).stem
        
        for algorithm, result in training_results.items():
            model_filename = f"{dataset_stem}_{algorithm}_model.joblib"
            model_path = MODELS_DIR / model_filename
            await ml_trainer.save_model(result["model"], model_path)
            model_files[algorithm] = model_filename
            logger.info(f"Saved {algorithm} model to: {model_filename}")
        
        # Calculate overall training time
        training_time = time.time() - start_time
        
        # Find best performing model
        best_algorithm = max(training_results.keys(), key=lambda k: training_results[k]["accuracy"])
        best_accuracy = training_results[best_algorithm]["accuracy"]
        target_met = best_accuracy >= ACCURACY_TARGET
        
        # Create clean response data with proper type conversion
        clean_results = {}
        for alg, result in training_results.items():
            clean_results[alg] = {
                "accuracy": float(result["accuracy"]),
                "precision": float(result.get("precision", 0)),
                "recall": float(result.get("recall", 0)),
                "f1_score": float(result.get("f1_score", 0)),
                "training_time": float(result.get("training_time", 0))
            }
        
        response_data = {
            "status": "success",
            "dataset_filename": str(request.dataset_filename),
            "algorithms_trained": list(training_results.keys()),
            "training_results": clean_results,
            "model_files": model_files,
            "best_algorithm": str(best_algorithm),
            "best_accuracy": float(best_accuracy),
            "accuracy_target_met": bool(target_met),  # Convert numpy bool_ to Python bool
            "training_time": float(training_time),
            "message": f"Training completed successfully. Best accuracy: {best_accuracy:.4f} ({best_algorithm})"
        }
        
        # Save training results
        results_filename = f"{dataset_stem}_training_results.json"
        results_path = RESULTS_DIR / results_filename
        with open(results_path, 'w') as f:
            import json
            json.dump(response_data, f, indent=2, default=str)
        
        logger.info(f"Training completed successfully. Models saved: {list(model_files.keys())}")
        return JSONResponse(content=response_data)
        
    except Exception as e:
        logger.error(f"Error training models: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
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
        model_stem = Path(model_filename).stem
        report_filename = f"{model_stem}_evaluation_report.json"
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

async def download_nsl_kdd_dataset():
    """Download and preprocess NSL-KDD dataset"""
    import urllib.request
    import subprocess
    import sys
    
    try:
        logger.info("Downloading NSL-KDD dataset...")
        
        # Run the download script
        script_path = "/app/download_nsl_kdd.py"
        if not Path(script_path).exists():
            # Create the download script in the container
            download_script = '''#!/usr/bin/env python3
import pandas as pd
import numpy as np
import urllib.request
import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NSL_KDD_URLS = {
    'train': 'https://raw.githubusercontent.com/defcom17/NSL_KDD/master/KDDTrain%2B.txt',
    'test': 'https://raw.githubusercontent.com/defcom17/NSL_KDD/master/KDDTest%2B.txt'
}

FEATURE_NAMES = [
    'duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes',
    'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in',
    'num_compromised', 'root_shell', 'su_attempted', 'num_root', 'num_file_creations',
    'num_shells', 'num_access_files', 'num_outbound_cmds', 'is_host_login',
    'is_guest_login', 'count', 'srv_count', 'serror_rate', 'srv_serror_rate',
    'rerror_rate', 'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate',
    'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count',
    'dst_host_same_srv_rate', 'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
    'dst_host_srv_diff_host_rate', 'dst_host_serror_rate', 'dst_host_srv_serror_rate',
    'dst_host_rerror_rate', 'dst_host_srv_rerror_rate', 'attack_type', 'difficulty'
]

ATTACK_TYPES = {
    'normal': 'normal',
    'back': 'attack', 'land': 'attack', 'neptune': 'attack', 'pod': 'attack',
    'smurf': 'attack', 'teardrop': 'attack', 'mailbomb': 'attack', 'apache2': 'attack',
    'processtable': 'attack', 'udpstorm': 'attack', 'satan': 'attack', 'ipsweep': 'attack', 
    'nmap': 'attack', 'portsweep': 'attack', 'mscan': 'attack', 'saint': 'attack',
    'guess_passwd': 'attack', 'ftp_write': 'attack', 'imap': 'attack', 'phf': 'attack',
    'multihop': 'attack', 'warezmaster': 'attack', 'warezclient': 'attack', 'spy': 'attack',
    'xlock': 'attack', 'xsnoop': 'attack', 'snmpread': 'attack', 'snmpwrite': 'attack',
    'httptunnel': 'attack', 'worm': 'attack', 'named': 'attack', 'sendmail': 'attack',
    'xterm': 'attack', 'ps': 'attack', 'sqlattack': 'attack', 'buffer_overflow': 'attack', 
    'loadmodule': 'attack', 'perl': 'attack', 'rootkit': 'attack'
}

def load_nsl_kdd_data(filepath):
    df = pd.read_csv(filepath, header=None, names=FEATURE_NAMES)
    df = df.drop('difficulty', axis=1)
    df['label'] = df['attack_type'].map(ATTACK_TYPES)
    df = df.drop('attack_type', axis=1)
    
    categorical_features = ['protocol_type', 'service', 'flag']
    for feature in categorical_features:
        if feature in df.columns:
            dummies = pd.get_dummies(df[feature], prefix=feature)
            df = pd.concat([df, dummies], axis=1)
            df = df.drop(feature, axis=1)
    
    numeric_columns = [col for col in df.columns if col != 'label']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.fillna(0)
    return df

def main():
    datasets_dir = Path('/app/datasets')
    datasets_dir.mkdir(exist_ok=True)
    
    train_file = datasets_dir / 'KDDTrain+.txt'
    test_file = datasets_dir / 'KDDTest+.txt'
    
    if not train_file.exists():
        logger.info("Downloading training data...")
        urllib.request.urlretrieve(NSL_KDD_URLS['train'], str(train_file))
    
    if not test_file.exists():
        logger.info("Downloading test data...")
        urllib.request.urlretrieve(NSL_KDD_URLS['test'], str(test_file))
    
    train_df = load_nsl_kdd_data(str(train_file))
    test_df = load_nsl_kdd_data(str(test_file))
    combined_df = pd.concat([train_df, test_df], ignore_index=True)
    combined_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Save full dataset
    output_file = datasets_dir / 'nsl_kdd_processed.csv'
    combined_df.to_csv(output_file, index=False)
    
    # Create sample dataset
    normal_samples = combined_df[combined_df['label'] == 'normal'].sample(n=min(4000, len(combined_df[combined_df['label'] == 'normal'])), random_state=42)
    attack_samples = combined_df[combined_df['label'] == 'attack'].sample(n=min(1000, len(combined_df[combined_df['label'] == 'attack'])), random_state=42)
    sample_df = pd.concat([normal_samples, attack_samples], ignore_index=True)
    sample_df = sample_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    sample_file = datasets_dir / 'nsl_kdd_sample.csv'
    sample_df.to_csv(sample_file, index=False)
    
    logger.info(f"NSL-KDD datasets created: {len(combined_df)} full, {len(sample_df)} sample")

if __name__ == "__main__":
    main()
'''
            with open(script_path, 'w') as f:
                f.write(download_script)
            os.chmod(script_path, 0o755)
        
        # Execute the download script
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, cwd="/app")
        
        if result.returncode != 0:
            logger.error(f"NSL-KDD download failed: {result.stderr}")
            raise Exception(f"NSL-KDD download failed: {result.stderr}")
        
        logger.info("NSL-KDD dataset downloaded successfully")
        
    except Exception as e:
        logger.error(f"Error downloading NSL-KDD dataset: {e}")
        raise

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=False,
        log_level="info"
    )
