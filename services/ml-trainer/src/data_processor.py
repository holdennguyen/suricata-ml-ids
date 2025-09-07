"""
Data Processor for ML Training
Handles data preparation and preprocessing for machine learning
"""

import logging
import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Handles data preprocessing and preparation for ML training
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = []
    
    async def prepare_training_data(
        self, 
        df: pd.DataFrame, 
        target_column: str = "label",
        test_size: float = 0.2
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Prepare training data from DataFrame
        """
        try:
            logger.info(f"Preparing training data with {len(df)} samples")
            
            # Separate features and target
            if target_column not in df.columns:
                raise ValueError(f"Target column '{target_column}' not found in data")
            
            # Get feature columns (exclude target)
            feature_columns = [col for col in df.columns if col != target_column]
            self.feature_names = feature_columns
            
            # Extract features and target
            X = df[feature_columns].values
            y = df[target_column].values
            
            # Handle missing values
            X = self._handle_missing_values(X)
            
            # Encode target labels if needed
            if y.dtype == 'object':
                y = self.label_encoder.fit_transform(y)
                logger.info(f"Encoded labels: {self.label_encoder.classes_}")
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            logger.info(f"Prepared data: {X_scaled.shape[0]} samples, {X_scaled.shape[1]} features")
            
            return X_scaled, y, self.feature_names
            
        except Exception as e:
            logger.error(f"Error preparing training data: {str(e)}")
            raise
    
    async def prepare_test_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Prepare test data using fitted scaler and encoder
        """
        try:
            if not self.feature_names:
                raise ValueError("DataProcessor not fitted. Call prepare_training_data first.")
            
            # Use same feature columns as training
            X = df[self.feature_names].values
            y = df.get('label', np.zeros(len(df)))
            
            # Handle missing values
            X = self._handle_missing_values(X)
            
            # Encode target labels if needed
            if hasattr(self.label_encoder, 'classes_') and y.dtype == 'object':
                y = self.label_encoder.transform(y)
            
            # Scale features using fitted scaler
            X_scaled = self.scaler.transform(X)
            
            return X_scaled, y, self.feature_names
            
        except Exception as e:
            logger.error(f"Error preparing test data: {str(e)}")
            raise
    
    def _handle_missing_values(self, X: np.ndarray) -> np.ndarray:
        """Handle missing values in feature matrix"""
        # Ensure all data is numeric first
        try:
            X = X.astype(float)
        except (ValueError, TypeError):
            # Handle mixed types by converting column by column
            for i in range(X.shape[1]):
                try:
                    X[:, i] = pd.to_numeric(X[:, i], errors='coerce')
                except:
                    # If conversion fails, fill with 0
                    X[:, i] = 0
        
        # Replace NaN with median for each feature
        for i in range(X.shape[1]):
            col = X[:, i].astype(float)
            if np.isnan(col).any():
                median_val = np.nanmedian(col)
                if np.isnan(median_val):
                    median_val = 0  # fallback if all values are NaN
                X[:, i] = np.where(np.isnan(col), median_val, col)
        
        return X.astype(float)
