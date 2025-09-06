"""
Detector Engine for Real-time Threat Detection
Implements ensemble prediction and threat scoring
"""

import logging
import time
import numpy as np
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class DetectorEngine:
    """
    Real-time threat detection engine using ensemble ML models
    """
    
    def __init__(self):
        self.models = {}
        self.model_weights = {}
        self.feature_names = []
        self.detection_history = deque(maxlen=1000)
        self.stats = {
            "detections_performed": 0,
            "threats_detected": 0,
            "total_processing_time": 0.0,
            "avg_processing_time_ms": 0.0
        }
    
    async def initialize(self, model_manager):
        """Initialize detector with available models"""
        try:
            self.models = model_manager.models
            self.model_weights = model_manager.get_model_weights()
            self.feature_names = model_manager.get_feature_names()
            
            logger.info(f"Detector initialized with {len(self.models)} models")
            
        except Exception as e:
            logger.error(f"Error initializing detector: {str(e)}")
            raise
    
    async def detect(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Perform real-time threat detection
        """
        start_time = time.time()
        
        try:
            # Convert features to numpy array
            feature_vector = self._prepare_feature_vector(features)
            
            # Get predictions from all models
            model_predictions = {}
            model_confidences = {}
            
            for model_name, model in self.models.items():
                try:
                    # Get prediction and confidence
                    prediction, confidence = await self._get_model_prediction(model, feature_vector)
                    model_predictions[model_name] = prediction
                    model_confidences[model_name] = confidence
                    
                except Exception as e:
                    logger.warning(f"Error getting prediction from {model_name}: {e}")
                    model_predictions[model_name] = "unknown"
                    model_confidences[model_name] = 0.0
            
            # Calculate ensemble prediction
            ensemble_result = self._calculate_ensemble_prediction(
                model_predictions, 
                model_confidences
            )
            
            # Calculate threat score
            threat_score = self._calculate_threat_score(
                model_predictions, 
                model_confidences, 
                features
            )
            
            # Update statistics
            processing_time = (time.time() - start_time) * 1000  # Convert to ms
            self._update_stats(processing_time, threat_score)
            
            result = {
                "prediction": ensemble_result["prediction"],
                "confidence": ensemble_result["confidence"],
                "threat_score": threat_score,
                "model_predictions": {
                    "predictions": model_predictions,
                    "confidences": model_confidences
                },
                "processing_time_ms": processing_time,
                "timestamp": time.time()
            }
            
            return result
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            logger.error(f"Error in threat detection: {str(e)} (took {processing_time:.1f}ms)")
            raise
    
    def _prepare_feature_vector(self, features: Dict[str, float]) -> np.ndarray:
        """Convert features dictionary to numpy array"""
        try:
            if not self.feature_names:
                # Use all available features if feature names not set
                feature_vector = np.array(list(features.values()))
            else:
                # Create vector in correct order
                feature_vector = np.zeros(len(self.feature_names))
                for i, feature_name in enumerate(self.feature_names):
                    feature_vector[i] = features.get(feature_name, 0.0)
            
            return feature_vector.reshape(1, -1)
            
        except Exception as e:
            logger.error(f"Error preparing feature vector: {str(e)}")
            raise
    
    async def _get_model_prediction(self, model, feature_vector: np.ndarray) -> tuple:
        """Get prediction and confidence from a single model"""
        try:
            # Get prediction
            prediction = model.predict(feature_vector)[0]
            
            # Get confidence/probability if available
            confidence = 0.5  # Default confidence
            
            if hasattr(model, 'predict_proba'):
                try:
                    probabilities = model.predict_proba(feature_vector)[0]
                    confidence = float(np.max(probabilities))
                except:
                    pass
            
            return prediction, confidence
            
        except Exception as e:
            logger.warning(f"Error getting model prediction: {str(e)}")
            return "unknown", 0.0
    
    def _calculate_ensemble_prediction(
        self, 
        model_predictions: Dict[str, Any], 
        model_confidences: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculate ensemble prediction from individual model predictions"""
        try:
            # Count predictions
            prediction_counts = defaultdict(float)
            total_confidence = 0.0
            
            for model_name, prediction in model_predictions.items():
                if prediction != "unknown":
                    confidence = model_confidences.get(model_name, 0.0)
                    weight = self.model_weights.get(model_name, 1.0)
                    
                    # Weighted vote
                    weighted_confidence = confidence * weight
                    prediction_counts[prediction] += weighted_confidence
                    total_confidence += weighted_confidence
            
            if not prediction_counts:
                return {"prediction": "unknown", "confidence": 0.0}
            
            # Get prediction with highest weighted confidence
            best_prediction = max(prediction_counts.items(), key=lambda x: x[1])
            ensemble_confidence = best_prediction[1] / total_confidence if total_confidence > 0 else 0.0
            
            return {
                "prediction": best_prediction[0],
                "confidence": ensemble_confidence
            }
            
        except Exception as e:
            logger.error(f"Error calculating ensemble prediction: {str(e)}")
            return {"prediction": "unknown", "confidence": 0.0}
    
    def _calculate_threat_score(
        self, 
        model_predictions: Dict[str, Any], 
        model_confidences: Dict[str, float],
        features: Dict[str, float]
    ) -> float:
        """Calculate overall threat score based on predictions and features"""
        try:
            # Base threat score from ensemble prediction
            threat_indicators = 0
            total_models = 0
            
            for model_name, prediction in model_predictions.items():
                if prediction != "unknown":
                    total_models += 1
                    if prediction == "attack" or prediction == 1:
                        confidence = model_confidences.get(model_name, 0.0)
                        weight = self.model_weights.get(model_name, 1.0)
                        threat_indicators += confidence * weight
            
            base_threat_score = threat_indicators / total_models if total_models > 0 else 0.0
            
            # Adjust based on feature anomalies
            anomaly_score = self._calculate_anomaly_score(features)
            
            # Combine scores
            final_threat_score = min(1.0, base_threat_score + anomaly_score * 0.2)
            
            return float(final_threat_score)
            
        except Exception as e:
            logger.error(f"Error calculating threat score: {str(e)}")
            return 0.0
    
    def _calculate_anomaly_score(self, features: Dict[str, float]) -> float:
        """Calculate anomaly score based on feature values"""
        try:
            anomaly_indicators = 0.0
            
            # Check for suspicious patterns
            if features.get("suspicious_flags", 0) > 5:
                anomaly_indicators += 0.3
            
            if features.get("packets_per_second", 0) > 100:
                anomaly_indicators += 0.2
            
            if features.get("tcp_syn_ratio", 0) > 0.8:
                anomaly_indicators += 0.2
            
            return min(1.0, anomaly_indicators)
            
        except Exception as e:
            logger.error(f"Error calculating anomaly score: {str(e)}")
            return 0.0
    
    def _update_stats(self, processing_time: float, threat_score: float):
        """Update detection statistics"""
        self.stats["detections_performed"] += 1
        self.stats["total_processing_time"] += processing_time
        self.stats["avg_processing_time_ms"] = (
            self.stats["total_processing_time"] / self.stats["detections_performed"]
        )
        
        if threat_score > 0.5:
            self.stats["threats_detected"] += 1
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get detection engine statistics"""
        return self.stats.copy()
