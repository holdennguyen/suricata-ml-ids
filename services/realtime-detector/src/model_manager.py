"""
Model Manager for Real-time Detector
Handles loading and managing ML models for real-time detection
"""

import logging
import joblib
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class ModelManager:
    """
    Manages ML models for real-time detection
    """
    
    def __init__(self):
        self.models = {}
        self.model_info = {}
        self.feature_names = []
        self.model_weights = {}
    
    async def load_models(self, models_dir: Path) -> None:
        """
        Load all available models from directory
        """
        try:
            if not models_dir.exists():
                logger.warning(f"Models directory not found: {models_dir}")
                return
            
            model_files = list(models_dir.glob("*.joblib"))
            
            if not model_files:
                logger.warning(f"No model files found in {models_dir}")
                return
            
            loaded_count = 0
            for model_file in model_files:
                try:
                    # Extract model name from filename
                    model_name = self._extract_model_name(model_file.name)
                    
                    # Load model
                    model = joblib.load(model_file)
                    self.models[model_name] = model
                    
                    # Store model info
                    self.model_info[model_name] = {
                        "filename": model_file.name,
                        "path": str(model_file),
                        "size_bytes": model_file.stat().st_size,
                        "algorithm": self._detect_algorithm(model)
                    }
                    
                    # Set default weight
                    self.model_weights[model_name] = 1.0
                    
                    loaded_count += 1
                    logger.info(f"Loaded model: {model_name} from {model_file.name}")
                    
                except Exception as e:
                    logger.error(f"Error loading model {model_file.name}: {str(e)}")
                    continue
            
            logger.info(f"Successfully loaded {loaded_count} models")
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise
    
    def _extract_model_name(self, filename: str) -> str:
        """Extract model name from filename"""
        # Remove .joblib extension and extract name
        name = filename.replace('.joblib', '')
        
        # Extract algorithm type from filename
        if 'decision_tree' in name:
            return 'decision_tree'
        elif 'knn' in name:
            return 'knn'
        elif 'ensemble' in name:
            return 'ensemble'
        else:
            return name
    
    def _detect_algorithm(self, model: Any) -> str:
        """Detect algorithm type from model object"""
        try:
            model_type = type(model).__name__.lower()
            
            if 'decisiontree' in model_type:
                return 'decision_tree'
            elif 'kneighbors' in model_type:
                return 'knn'
            elif 'voting' in model_type:
                return 'ensemble'
            elif 'pipeline' in model_type:
                return 'pipeline'
            else:
                return model_type
                
        except Exception as e:
            logger.warning(f"Could not detect algorithm type: {e}")
            return 'unknown'
    
    def get_model_info(self) -> List[Dict[str, Any]]:
        """Get information about all loaded models"""
        return [
            {
                "name": name,
                "algorithm": info["algorithm"],
                "filename": info["filename"],
                "size_bytes": info["size_bytes"]
            }
            for name, info in self.model_info.items()
        ]
    
    def get_model_weights(self) -> Dict[str, float]:
        """Get current model weights"""
        return self.model_weights.copy()
    
    def get_feature_names(self) -> List[str]:
        """Get feature names used by models"""
        return self.feature_names.copy()
    
    def get_loaded_models(self) -> List[str]:
        """Get list of loaded model names"""
        return list(self.models.keys())
