"""Model training module."""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import joblib
import mlflow
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score

from mlops_production_system.config.settings import settings
from mlops_production_system.utils.logging_utils import get_logger

logger = get_logger(__name__)


class ModelTrainer:
    """Model trainer class."""

    def __init__(
        self,
        model_type: str = "random_forest",
        hyperparameters: Optional[Dict[str, Any]] = None,
        experiment_name: Optional[str] = None,
        mlflow_tracking_uri: Optional[str] = None,
    ):
        """Initialize model trainer.
        
        Args:
            model_type: Type of model to train.
            hyperparameters: Model hyperparameters.
            experiment_name: MLflow experiment name.
            mlflow_tracking_uri: MLflow tracking URI.
        """
        self.model_type = model_type
        self.hyperparameters = hyperparameters or {}
        self.experiment_name = experiment_name or settings.MLFLOW.EXPERIMENT_NAME
        self.mlflow_tracking_uri = mlflow_tracking_uri or settings.MLFLOW.TRACKING_URI
        self.model = None
        
        # Configure MLflow
        if self.mlflow_tracking_uri:
            mlflow.set_tracking_uri(self.mlflow_tracking_uri)
            logger.info(f"MLflow tracking URI set to {self.mlflow_tracking_uri}")
        
        # Create MLflow experiment if it doesn't exist
        try:
            self.experiment_id = mlflow.create_experiment(
                self.experiment_name,
                artifact_location=os.path.join(settings.MLFLOW.MODEL_REGISTRY, self.experiment_name)
            )
            logger.info(f"Created new MLflow experiment: {self.experiment_name}")
        except mlflow.exceptions.MlflowException:
            self.experiment_id = mlflow.get_experiment_by_name(self.experiment_name).experiment_id
            logger.info(f"Using existing MLflow experiment: {self.experiment_name}")

    def _get_model_instance(self) -> BaseEstimator:
        """Get model instance based on model type.
        
        Returns:
            Model instance.
            
        Raises:
            ValueError: If model type is not supported.
        """
        if self.model_type == "random_forest":
            return RandomForestClassifier(**self.hyperparameters)
        elif self.model_type == "gradient_boosting":
            return GradientBoostingClassifier(**self.hyperparameters)
        elif self.model_type == "logistic_regression":
            return LogisticRegression(**self.hyperparameters)
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")

    def train(
        self,
        X_train: Union[np.ndarray, pd.DataFrame],
        y_train: Union[np.ndarray, pd.Series],
        X_val: Optional[Union[np.ndarray, pd.DataFrame]] = None,
        y_val: Optional[Union[np.ndarray, pd.Series]] = None,
    ) -> BaseEstimator:
        """Train model.
        
        Args:
            X_train: Training features.
            y_train: Training target.
            X_val: Validation features.
            y_val: Validation target.
        
        Returns:
            Trained model.
        """
        logger.info(f"Training {self.model_type} model...")
        
        # Get model instance
        self.model = self._get_model_instance()
        
        # Start MLflow run
        with mlflow.start_run(experiment_id=self.experiment_id) as run:
            run_id = run.info.run_id
            logger.info(f"MLflow run ID: {run_id}")
            
            # Log hyperparameters
            mlflow.log_params(self.hyperparameters)
            mlflow.log_param("model_type", self.model_type)
            
            # Train model
            self.model.fit(X_train, y_train)
            
            # Evaluate on training set
            train_metrics = self.evaluate(X_train, y_train, prefix="train_")
            
            # Log training metrics
            for metric_name, metric_value in train_metrics.items():
                mlflow.log_metric(metric_name, metric_value)
            
            # Evaluate on validation set if provided
            if X_val is not None and y_val is not None:
                val_metrics = self.evaluate(X_val, y_val, prefix="val_")
                
                # Log validation metrics
                for metric_name, metric_value in val_metrics.items():
                    mlflow.log_metric(metric_name, metric_value)
            
            # Log model
            mlflow.sklearn.log_model(
                self.model,
                artifact_path="model",
                registered_model_name=f"{self.experiment_name}_{self.model_type}"
            )
            
            logger.info(f"Model training completed. Run ID: {run_id}")
            
        return self.model

    def evaluate(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y_true: Union[np.ndarray, pd.Series],
        prefix: str = "",
    ) -> Dict[str, float]:
        """Evaluate model.
        
        Args:
            X: Features.
            y_true: True target.
            prefix: Prefix for metric names.
        
        Returns:
            Evaluation metrics.
            
        Raises:
            ValueError: If model is not trained.
        """
        if self.model is None:
            raise ValueError("Model is not trained. Call train first.")
            
        # Get predictions
        y_pred = self.model.predict(X)
        y_pred_proba = None
        
        # Get probability predictions if model supports it
        try:
            y_pred_proba = self.model.predict_proba(X)[:, 1]
        except (AttributeError, IndexError):
            logger.warning("Model does not support predict_proba.")
        
        # Calculate metrics
        metrics = {}
        metrics[f"{prefix}accuracy"] = accuracy_score(y_true, y_pred)
        metrics[f"{prefix}f1"] = f1_score(y_true, y_pred, average="weighted")
        metrics[f"{prefix}precision"] = precision_score(y_true, y_pred, average="weighted")
        metrics[f"{prefix}recall"] = recall_score(y_true, y_pred, average="weighted")
        
        # Calculate ROC AUC if probability predictions are available
        if y_pred_proba is not None:
            try:
                metrics[f"{prefix}roc_auc"] = roc_auc_score(y_true, y_pred_proba)
            except ValueError:
                logger.warning("Could not calculate ROC AUC score.")
        
        logger.info(f"Evaluation metrics: {metrics}")
        
        return metrics

    def save_model(self, output_path: Optional[str] = None) -> str:
        """Save model to file.
        
        Args:
            output_path: Path to save model.
        
        Returns:
            Path to saved model.
            
        Raises:
            ValueError: If model is not trained.
        """
        if self.model is None:
            raise ValueError("Model is not trained. Call train first.")
            
        # Determine output path
        if output_path is None:
            model_dir = Path(settings.MODEL.MODEL_DIR)
            model_dir.mkdir(parents=True, exist_ok=True)
            output_path = str(model_dir / f"{self.model_type}_model.joblib")
        
        # Save model
        joblib.dump(self.model, output_path)
        logger.info(f"Model saved to {output_path}")
        
        return output_path

    def load_model(self, model_path: str) -> BaseEstimator:
        """Load model from file.
        
        Args:
            model_path: Path to model file.
        
        Returns:
            Loaded model.
            
        Raises:
            FileNotFoundError: If model file does not exist.
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file {model_path} does not exist.")
            
        # Load model
        self.model = joblib.load(model_path)
        logger.info(f"Model loaded from {model_path}")
        
        return self.model

    def predict(
        self, X: Union[np.ndarray, pd.DataFrame]
    ) -> Union[np.ndarray, List]:
        """Make predictions with trained model.
        
        Args:
            X: Features.
        
        Returns:
            Predictions.
            
        Raises:
            ValueError: If model is not trained.
        """
        if self.model is None:
            raise ValueError("Model is not trained. Call train first.")
            
        return self.model.predict(X)

    def predict_proba(
        self, X: Union[np.ndarray, pd.DataFrame]
    ) -> Union[np.ndarray, List]:
        """Make probability predictions with trained model.
        
        Args:
            X: Features.
        
        Returns:
            Probability predictions.
            
        Raises:
            ValueError: If model is not trained.
            AttributeError: If model does not support predict_proba.
        """
        if self.model is None:
            raise ValueError("Model is not trained. Call train first.")
            
        return self.model.predict_proba(X)


# Factory function for easy instantiation
def get_model_trainer(
    model_type: str = "random_forest",
    hyperparameters: Optional[Dict[str, Any]] = None,
    experiment_name: Optional[str] = None,
    mlflow_tracking_uri: Optional[str] = None,
) -> ModelTrainer:
    """Get a ModelTrainer instance.
    
    Args:
        model_type: Type of model to train.
        hyperparameters: Model hyperparameters.
        experiment_name: MLflow experiment name.
        mlflow_tracking_uri: MLflow tracking URI.
    
    Returns:
        ModelTrainer instance.
    """
    return ModelTrainer(
        model_type=model_type,
        hyperparameters=hyperparameters,
        experiment_name=experiment_name,
        mlflow_tracking_uri=mlflow_tracking_uri,
    )
