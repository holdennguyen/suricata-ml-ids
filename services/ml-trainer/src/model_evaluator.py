"""
Model Evaluator for ML Training
Handles model evaluation and performance metrics
"""

import logging
import numpy as np
from typing import Dict, Any, List
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)

logger = logging.getLogger(__name__)

class ModelEvaluator:
    """
    Handles model evaluation and performance metrics calculation
    """
    
    def __init__(self):
        self.metrics_history = []
    
    async def evaluate_model(
        self, 
        model: Any, 
        X_test: np.ndarray, 
        y_test: np.ndarray
    ) -> Dict[str, Any]:
        """
        Evaluate a trained model on test data
        """
        try:
            logger.info(f"Evaluating model on {len(X_test)} test samples")
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate basic metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
            recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
            f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
            
            # Calculate confusion matrix
            cm = confusion_matrix(y_test, y_pred)
            
            # Generate classification report
            class_report = classification_report(
                y_test, y_pred, 
                output_dict=True, 
                zero_division=0
            )
            
            # Store metrics
            evaluation_results = {
                "accuracy": float(accuracy),
                "precision": float(precision),
                "recall": float(recall),
                "f1_score": float(f1),
                "confusion_matrix": cm.tolist(),
                "classification_report": class_report,
                "test_samples": len(X_test),
                "unique_classes": len(np.unique(y_test))
            }
            
            # Store in history
            self.metrics_history.append(evaluation_results)
            
            logger.info(f"Model evaluation completed. Accuracy: {accuracy:.4f}")
            
            return evaluation_results
            
        except Exception as e:
            logger.error(f"Error evaluating model: {str(e)}")
            raise
