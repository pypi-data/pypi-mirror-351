from .dataset import Dataset
from .chaos_classifier import ChaosClassifier
from .model_wrapper import ModelWrapper
from typing import Dict, Any, Optional, Union, List
import json
import numpy as np
import os
import glob
import pickle

# Disable tokenizers parallelism warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

class AerylModel:
    """A wrapper class that provides a high-level interface for training and inference using the chaos classifier."""
    
    def __init__(self, 
                 dev_path: str = 'data/company_research_dev.csv', 
                 prod_path: str = 'data/company_research_prod.csv',
                 models_dir: str = 'models',
                 model_id: Optional[str] = None):
        """Initialize the AerylModel.
        
        Args:
            dev_path: Path to the development dataset CSV file
            prod_path: Path to the production dataset CSV file
            models_dir: Directory to save/load models
            model_id: Optional model ID to load an existing model
        """
        self.dev_path = dev_path
        self.prod_path = prod_path
        self.models_dir = models_dir
        self.dev_dataset = None
        self.prod_dataset = None
        self.classifier = None
        self.model_id = None
        self._model_wrappers = {}  # Dictionary to store ModelWrapper instances
        
        # If model_id is provided, load the model
        if model_id:
            self.load_model(model_id)
        
    def _serialize_for_json(self, obj: Any) -> Any:
        """Serialize objects for JSON compatibility."""
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: self._serialize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._serialize_for_json(item) for item in obj]
        elif isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif hasattr(obj, '__dict__'):
            return self._serialize_for_json(obj.__dict__)
        return str(obj)
        
    def train(self) -> Dict[str, Any]:
        """Train the model on the development dataset."""
        self.dev_dataset = Dataset(self.dev_path)
        self.dev_dataset.prepare_for_training()
        
        self.classifier = ChaosClassifier(self.dev_dataset)
        training_results = self.classifier.train_and_save(self.models_dir)
        
        # Store the model ID
        self.model_id = training_results['model_id']
        
        # Create model wrappers for each step
        self._model_wrappers = {}
        for step, model in self.classifier.models.items():
            feature_names = model.feature_names if hasattr(model, 'feature_names') else []
            feature_importance = self.classifier.feature_importance.get(step, {})
            performance_metrics = self.classifier.performance.get(step, {})
            
            # Create model wrapper
            self._model_wrappers[step] = ModelWrapper(
                model=model,
                feature_names=feature_names,
                feature_importance=feature_importance,
                performance_metrics=performance_metrics
            )
        
        return {
            'model_id': self.model_id,
        }
        
    def predict(self, model_id: Optional[str] = None) -> Dict[str, Any]:
        """Perform inference on the production dataset.
        
        Args:
            model_id: Optional specific model ID to use for prediction. If None, uses the most recent model.
            
        Returns:
            Dictionary containing predictions and model information
            Example: {
                'model_id': 'uuid-123',
                'predictions': {
                    'run_1': {
                        'step_1': {'prediction': True, 'probability': 0.85},
                        'step_2': {'prediction': False, 'probability': 0.12},
                        'step_3': {'prediction': True, 'probability': 0.92}
                    },
                    'run_2': {
                        'step_1': {'prediction': False, 'probability': 0.08},
                        'step_2': {'prediction': False, 'probability': 0.15},
                        'step_3': {'prediction': False, 'probability': 0.23}
                    }
                }
            }
        """
        # Initialize classifier if needed
        if self.classifier is None:
            self.classifier = ChaosClassifier(self.dev_dataset)
            
        # Load production dataset
        self.prod_dataset = Dataset(self.prod_path)
        self.prod_dataset.prepare_for_inference()
        
        # Get predictions from classifier
        raw_predictions = self.classifier.load_and_predict(
            self.prod_dataset, 
            self.dev_dataset, 
            self.models_dir, 
            model_id
        )
        # Store the model ID if one was loaded
        if model_id:
            self.model_id = model_id
            
        # Create model wrappers for each step
        self._model_wrappers = {}
        for step, model in self.classifier.models.items():
            feature_names = model.feature_names if hasattr(model, 'feature_names') else []
            feature_importance = self.classifier.feature_importance.get(step, {})
            performance_metrics = self.classifier.performance.get(step, {})
            
            self._model_wrappers[step] = ModelWrapper(
                model=model,
                feature_names=feature_names,
                feature_importance=feature_importance,
                performance_metrics=performance_metrics
            )
        
        # Create simplified prediction structure with calibrated probabilities
        simplified_predictions = {}
        for run_id in self.prod_dataset.dataframe['run_id']:
            run_id = str(run_id)
            if run_id in raw_predictions:
                simplified_predictions[run_id] = {}
                for step in range(1, self.classifier.num_steps + 1):
                    step_key = f'step_{step}'
                    if step_key in raw_predictions[run_id]:
                        # Get the raw probability and prediction directly
                        simplified_predictions[run_id][step_key] = {
                            'prediction': bool(raw_predictions[run_id][step_key]['prediction']),
                            'probability': float(raw_predictions[run_id][step_key]['probability'])
                        }
        
        return {
            'model_id': self.model_id,
            'predictions': simplified_predictions
        }
        
    def list_models(self) -> List[Dict[str, Any]]:
        """List all available trained models with their metadata.
        
        Returns:
            List of dictionaries containing model information including ID, timestamp, and performance metrics.
        """
        if not os.path.exists(self.models_dir):
            return []
            
        models = []
        for model_dir in glob.glob(os.path.join(self.models_dir, '*')):
            if not os.path.isdir(model_dir):
                continue
                
            metadata_path = os.path.join(model_dir, 'metadata.pkl')
            if not os.path.exists(metadata_path):
                continue
                
            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)
                
            models.append({
                'model_id': metadata['model_id'],
                'timestamp': metadata['timestamp'],
                'num_steps': metadata['num_steps'],
                'performance': self._serialize_for_json(metadata['performance'])
            })
            
        # Sort by timestamp, most recent first
        return sorted(models, key=lambda x: x['timestamp'], reverse=True)
        
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific model.
        
        Args:
            model_id: The ID of the model to get information about.
            
        Returns:
            Dictionary containing detailed model information.
        """
        model_dir = os.path.join(self.models_dir, model_id)
        if not os.path.exists(model_dir):
            raise ValueError(f"No model found with ID {model_id}")
            
        metadata_path = os.path.join(model_dir, 'metadata.pkl')
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
            
        return {
            'model_id': metadata['model_id'],
            'timestamp': metadata['timestamp'],
            'num_steps': metadata['num_steps'],
            'performance': self._serialize_for_json(metadata['performance'])
        }
        
    def delete_model(self, model_id: str) -> bool:
        """Delete a specific model.
        
        Args:
            model_id: The ID of the model to delete.
            
        Returns:
            True if the model was successfully deleted, False otherwise.
        """
        model_dir = os.path.join(self.models_dir, model_id)
        if not os.path.exists(model_dir):
            return False
            
        import shutil
        shutil.rmtree(model_dir)
        return True
        
    def get_performance_metrics(self, step: Optional[int] = None) -> Dict[str, Any]:
        """Get performance metrics for the model."""
        if self.classifier is None:
            raise ValueError("Model not trained. Call train() first.")
        return self._serialize_for_json(self.classifier.performance_metrics(step))
        
    def get_step_model(self, step: int) -> ModelWrapper:
        """Get the model wrapper for a specific step.
        
        Args:
            step: The step number to get the model for
            
        Returns:
            ModelWrapper instance for the specified step
        """
        if not self._model_wrappers:
            raise ValueError("No models available. Call train() or predict() first.")
            
        if step not in self._model_wrappers:
            raise ValueError(f"No model found for step {step}")
            
        return self._model_wrappers[step]
        
    def get_step_model_info(self, step: int) -> Dict[str, Any]:
        """Get detailed information about a specific step model.
        
        Args:
            step: The step number to get information for
            
        Returns:
            Dictionary containing model information
        """
        model_wrapper = self.get_step_model(step)
        return model_wrapper.get_model_summary()
        
    def describe_datasets(self) -> Dict[str, Any]:
        """Get a description of both development and production datasets.
        
        Returns:
            Dictionary containing statistics for both datasets:
            {
                'development': {
                    'num_runs': int,          # Total number of runs
                    'num_steps': int,         # Number of steps per run
                    'error_free_runs': int,   # Number of runs without errors
                    'error_runs': int,        # Number of runs with errors
                    'training_rows': int,     # Number of training data points
                    'unique_runs': int,       # Number of unique runs
                    'error_free_pairs': int,  # Number of error-free pairs
                    'error_pairs': int        # Number of error pairs
                },
                'production': {
                    'num_runs': int,          # Total number of runs
                    'num_steps': int          # Number of steps per run
                }
            }
        """
        # Initialize datasets if not already done
        if self.dev_dataset is None:
            self.dev_dataset = Dataset(self.dev_path)
        if self.prod_dataset is None:
            self.prod_dataset = Dataset(self.prod_path)
            
        # Get descriptions
        dev_stats = self.dev_dataset.describe()
        prod_stats = self.prod_dataset.describe()
        
        return {
            'development': dev_stats,
            'production': prod_stats
        }
        
    def to_json(self) -> str:
        """Convert the model's current state to a JSON string.
        
        Returns:
            JSON string containing:
            - Basic model info (paths, training status)
            - Dataset statistics (if trained)
            - Performance metrics (if trained)
        """
        state = {
            'dev_path': self.dev_path,
            'prod_path': self.prod_path,
            'models_dir': self.models_dir,
            'is_trained': self.classifier is not None
        }
        
        if self.classifier is not None:
            state.update({
                'dataset_stats': self.describe_datasets(),
                'performance_metrics': self.get_performance_metrics()
            })
            
        return json.dumps(state, indent=2)
        
    @classmethod
    def from_json(cls, json_str: str) -> 'AerylModel':
        """Create an AerylModel instance from a JSON string."""
        state = json.loads(json_str)
        model = cls(
            dev_path=state['dev_path'],
            prod_path=state['prod_path'],
            models_dir=state['models_dir']
        )
        
        if state['is_trained']:
            model.train()
            
        return model
        
    def load_model(self, model_id: str) -> None:
        """Load a trained model by ID.
        
        Args:
            model_id: The ID of the model to load
            
        Raises:
            ValueError: If the model is not found
        """
        # Initialize classifier if needed
        if self.classifier is None:
            self.dev_dataset = Dataset(self.dev_path)
            self.classifier = ChaosClassifier(self.dev_dataset)
            
        # Load the model
        self.classifier.load_models(self.models_dir, model_id)
        self.model_id = model_id
        
        # Create model wrappers for each step
        self._model_wrappers = {}
        for step, model in self.classifier.models.items():
            feature_names = model.feature_names if hasattr(model, 'feature_names') else []
            feature_importance = self.classifier.feature_importance.get(step, {})
            performance_metrics = self.classifier.performance.get(step, {})
            
            self._model_wrappers[step] = ModelWrapper(
                model=model,
                feature_names=feature_names,
                feature_importance=feature_importance,
                performance_metrics=performance_metrics
            ) 