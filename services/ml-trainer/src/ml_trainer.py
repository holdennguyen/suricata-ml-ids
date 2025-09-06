"""
ML Training Engine for Network Intrusion Detection
Implements Decision Tree, k-NN, and Ensemble models
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import time

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import VotingClassifier, RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler
import joblib

logger = logging.getLogger(__name__)

class MLTrainer:
    """
    Machine Learning trainer for network intrusion detection
    Supports Decision Tree, k-NN, and Ensemble methods
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.random_state = 42
    
    async def train_decision_tree(
        self, 
        X: np.ndarray, 
        y: np.ndarray, 
        feature_names: List[str],
        hyperparameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Train Decision Tree classifier
        
        Args:
            X: Feature matrix
            y: Target labels
            feature_names: List of feature names
            hyperparameters: Optional hyperparameter overrides
            
        Returns:
            Dictionary with training results
        """
        try:
            logger.info("Training Decision Tree classifier...")
            start_time = time.time()
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=self.random_state, stratify=y
            )
            
            # Default hyperparameters
            default_params = {
                'max_depth': [10, 20, 30, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4],
                'criterion': ['gini', 'entropy']
            }
            
            if hyperparameters:
                default_params.update(hyperparameters)
            
            # Create base model
            dt = DecisionTreeClassifier(random_state=self.random_state)
            
            # Grid search for best parameters
            grid_search = GridSearchCV(
                dt, 
                default_params, 
                cv=5, 
                scoring='accuracy',
                n_jobs=-1,
                verbose=1
            )
            
            grid_search.fit(X_train, y_train)
            best_model = grid_search.best_estimator_
            
            # Evaluate model
            y_pred = best_model.predict(X_test)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted')
            recall = recall_score(y_test, y_pred, average='weighted')
            f1 = f1_score(y_test, y_pred, average='weighted')
            
            # Cross-validation
            cv_scores = cross_val_score(best_model, X, y, cv=5)
            
            # Feature importance
            feature_importance = dict(zip(
                feature_names, 
                best_model.feature_importances_
            ))
            
            # Sort features by importance
            sorted_features = sorted(
                feature_importance.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            training_time = time.time() - start_time
            
            result = {
                'model': best_model,
                'algorithm': 'decision_tree',
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'best_params': grid_search.best_params_,
                'feature_importance': feature_importance,
                'top_features': sorted_features[:10],
                'training_time': training_time
            }
            
            logger.info(f"Decision Tree training completed. Accuracy: {accuracy:.4f}")
            return result
            
        except Exception as e:
            logger.error(f"Error training Decision Tree: {str(e)}")
            raise
    
    async def train_knn(
        self, 
        X: np.ndarray, 
        y: np.ndarray, 
        feature_names: List[str],
        hyperparameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Train k-NN classifier
        
        Args:
            X: Feature matrix
            y: Target labels
            feature_names: List of feature names
            hyperparameters: Optional hyperparameter overrides
            
        Returns:
            Dictionary with training results
        """
        try:
            logger.info("Training k-NN classifier...")
            start_time = time.time()
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=self.random_state, stratify=y
            )
            
            # Scale features (important for k-NN)
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Default hyperparameters
            default_params = {
                'n_neighbors': [3, 5, 7, 9, 11],
                'weights': ['uniform', 'distance'],
                'metric': ['euclidean', 'manhattan', 'minkowski']
            }
            
            if hyperparameters:
                default_params.update(hyperparameters)
            
            # Create base model
            knn = KNeighborsClassifier()
            
            # Grid search for best parameters
            grid_search = GridSearchCV(
                knn, 
                default_params, 
                cv=5, 
                scoring='accuracy',
                n_jobs=-1,
                verbose=1
            )
            
            grid_search.fit(X_train_scaled, y_train)
            best_model = grid_search.best_estimator_
            
            # Evaluate model
            y_pred = best_model.predict(X_test_scaled)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted')
            recall = recall_score(y_test, y_pred, average='weighted')
            f1 = f1_score(y_test, y_pred, average='weighted')
            
            # Cross-validation on scaled data
            X_scaled = self.scaler.fit_transform(X)
            cv_scores = cross_val_score(best_model, X_scaled, y, cv=5)
            
            training_time = time.time() - start_time
            
            # Create a pipeline model that includes scaling
            from sklearn.pipeline import Pipeline
            pipeline_model = Pipeline([
                ('scaler', self.scaler),
                ('knn', best_model)
            ])
            
            # Fit the pipeline
            pipeline_model.fit(X, y)
            
            result = {
                'model': pipeline_model,
                'algorithm': 'knn',
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'best_params': grid_search.best_params_,
                'training_time': training_time
            }
            
            logger.info(f"k-NN training completed. Accuracy: {accuracy:.4f}")
            return result
            
        except Exception as e:
            logger.error(f"Error training k-NN: {str(e)}")
            raise
    
    async def train_ensemble(
        self, 
        X: np.ndarray, 
        y: np.ndarray, 
        feature_names: List[str],
        hyperparameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Train ensemble classifier (combines Decision Tree and k-NN)
        
        Args:
            X: Feature matrix
            y: Target labels
            feature_names: List of feature names
            hyperparameters: Optional hyperparameter overrides
            
        Returns:
            Dictionary with training results
        """
        try:
            logger.info("Training Ensemble classifier...")
            start_time = time.time()
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=self.random_state, stratify=y
            )
            
            # Create base models
            dt = DecisionTreeClassifier(
                max_depth=20, 
                min_samples_split=5,
                random_state=self.random_state
            )
            
            from sklearn.pipeline import Pipeline
            knn_pipeline = Pipeline([
                ('scaler', StandardScaler()),
                ('knn', KNeighborsClassifier(n_neighbors=5, weights='distance'))
            ])
            
            # Add Random Forest for better ensemble
            rf = RandomForestClassifier(
                n_estimators=100,
                max_depth=20,
                random_state=self.random_state
            )
            
            # Create voting classifier
            ensemble = VotingClassifier(
                estimators=[
                    ('dt', dt),
                    ('knn', knn_pipeline),
                    ('rf', rf)
                ],
                voting='soft'
            )
            
            # Apply hyperparameters if provided
            if hyperparameters:
                if 'voting' in hyperparameters:
                    ensemble.voting = hyperparameters['voting']
            
            # Train ensemble
            ensemble.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = ensemble.predict(X_test)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted')
            recall = recall_score(y_test, y_pred, average='weighted')
            f1 = f1_score(y_test, y_pred, average='weighted')
            
            # Cross-validation
            cv_scores = cross_val_score(ensemble, X, y, cv=5)
            
            # Get individual model accuracies
            individual_accuracies = {}
            for name, model in ensemble.named_estimators_.items():
                model.fit(X_train, y_train)
                pred = model.predict(X_test)
                individual_accuracies[name] = accuracy_score(y_test, pred)
            
            training_time = time.time() - start_time
            
            result = {
                'model': ensemble,
                'algorithm': 'ensemble',
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'individual_accuracies': individual_accuracies,
                'ensemble_improvement': accuracy - max(individual_accuracies.values()),
                'training_time': training_time
            }
            
            logger.info(f"Ensemble training completed. Accuracy: {accuracy:.4f}")
            return result
            
        except Exception as e:
            logger.error(f"Error training Ensemble: {str(e)}")
            raise
    
    async def save_model(self, model: Any, model_path: Path) -> None:
        """
        Save trained model to disk
        
        Args:
            model: Trained model object
            model_path: Path to save the model
        """
        try:
            model_path.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(model, model_path)
            logger.info(f"Model saved to: {model_path}")
            
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            raise
    
    async def load_model(self, model_path: Path) -> Any:
        """
        Load trained model from disk
        
        Args:
            model_path: Path to the saved model
            
        Returns:
            Loaded model object
        """
        try:
            if not model_path.exists():
                raise FileNotFoundError(f"Model file not found: {model_path}")
            
            model = joblib.load(model_path)
            logger.info(f"Model loaded from: {model_path}")
            return model
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
