from typing import Dict, Any, List, Optional
import xgboost as xgb
import numpy as np

class ModelWrapper:
    """A wrapper class that encapsulates XGBoost model functionality and masks internal details."""
    
    def __init__(self, model: xgb.Booster, feature_names: List[str], 
                 feature_importance: Dict[str, float], performance_metrics: Dict[str, Any]):
        """Initialize the ModelWrapper.
        
        Args:
            model: The XGBoost model to wrap
            feature_names: List of feature names used by the model
            feature_importance: Dictionary of feature importance scores
            performance_metrics: Dictionary of performance metrics
        """
        self._model = model
        self._feature_names = feature_names
        self._feature_importance = feature_importance
        self._performance_metrics = performance_metrics
        
    def predict(self, features: np.ndarray) -> np.ndarray:
        """Make predictions using the model.
        
        Args:
            features: Input features as a numpy array
            
        Returns:
            Array of prediction probabilities
        """
        dmatrix = xgb.DMatrix(features, feature_names=self._feature_names)
        return self._model.predict(dmatrix)
    
    def predict_binary(self, features: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        """Make binary predictions using the model.
        
        Args:
            features: Input features as a numpy array
            threshold: Probability threshold for binary classification
            
        Returns:
            Array of binary predictions (0 or 1)
        """
        probabilities = self.predict(features)
        return (probabilities > threshold).astype(int)
    
    def _convert_to_serializable(self, obj: Any) -> Any:
        """Convert objects to JSON serializable format."""
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: self._convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._convert_to_serializable(item) for item in obj]
        return obj
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get model performance metrics.
        
        Returns:
            Dictionary of performance metrics
        """
        return self._convert_to_serializable(self._performance_metrics)
    
    def get_model_summary(self) -> Dict[str, Any]:
        """Get a summary of the model's characteristics.
        
        Returns:
            Dictionary containing model summary information
        """
        return {
            'num_features': len(self._feature_names),
            'performance_metrics': self._convert_to_serializable(self._performance_metrics)
        } 