"""
Pydantic models for ML Trainer Service API
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class TrainingRequest(BaseModel):
    """Request model for ML training"""
    dataset_filename: str = Field(..., description="Name of the dataset file")
    algorithms: List[str] = Field(..., description="List of algorithms to train")
    target_column: str = Field(default="label", description="Name of target column")
    test_size: float = Field(default=0.2, description="Fraction of data for testing")
    hyperparameters: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Algorithm-specific hyperparameters")

class TrainingResponse(BaseModel):
    """Response model for ML training"""
    dataset_filename: str = Field(..., description="Name of the processed dataset")
    algorithms_trained: List[str] = Field(..., description="List of successfully trained algorithms")
    training_results: Dict[str, Any] = Field(..., description="Training results for each algorithm")
    model_files: Dict[str, str] = Field(..., description="Generated model filenames")
    best_algorithm: str = Field(..., description="Best performing algorithm")
    best_accuracy: float = Field(..., description="Best accuracy achieved")
    accuracy_target_met: bool = Field(..., description="Whether accuracy target was met")
    training_time: float = Field(..., description="Total training time in seconds")

class EvaluationResponse(BaseModel):
    """Response model for model evaluation"""
    model_filename: str = Field(..., description="Name of the evaluated model file")
    test_dataset_filename: str = Field(..., description="Name of the test dataset")
    evaluation_results: Dict[str, Any] = Field(..., description="Detailed evaluation results")
    report_filename: str = Field(..., description="Generated evaluation report filename")
