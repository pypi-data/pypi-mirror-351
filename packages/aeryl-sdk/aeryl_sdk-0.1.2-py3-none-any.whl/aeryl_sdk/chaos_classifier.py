from .dataset import Dataset
import xgboost as xgb
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, confusion_matrix, roc_auc_score, accuracy_score
import numpy as np
import polars as pl
from tqdm import tqdm
from .metrics import embedding_model, process_paths
import os
import uuid
import datetime

class ChaosClassifier:
    def __init__(self, dataset: Dataset):
        self.dataset = dataset
        self.stats = dataset.describe()
        self.num_steps = self.stats['num_steps']
        self.models = {}  # Dictionary to store models for each step
        self.feature_importance = {}  # Dictionary to store feature importance for each model
        self.performance = {}  # Dictionary to store performance metrics for each model
        self.model_id = None  # Unique ID for this model instance
        self.validation_data = {}  # Dictionary to store validation data for each step

    def train(self):
        """Train XGBoost models for each step."""
        if not hasattr(self.dataset, 'features_df'):
            raise ValueError("Dataset features not calculated. Call calculate_features() first.")
            
        features_df = self.dataset.features_df
        if features_df.is_empty():
            raise ValueError("Features DataFrame is empty")
        
        # Generate all features
        features_df = self._generate_features(features_df)
            
        # Train a model for each step
        for step in tqdm(range(1, self.num_steps + 1), desc="Training models for each step"):
            # Prepare features for this step
            step_features = self._prepare_step_features(features_df, step)
            
            # Verify all features exist
            missing_features = [f for f in step_features if f not in features_df.columns]
            if missing_features:
                raise ValueError(f"Missing features for step {step}: {missing_features}")
            
            # Prepare features and target for this step
            step_features.append('has_error')  # Add has_error to features for filtering
            X = features_df.select(step_features)
            y = features_df.select('has_error')
            
            # Convert data types and handle missing values
            for col in X.columns:
                if col == 'has_error':
                    continue  # Skip has_error column
                if col.startswith('exponent_'):
                    # Convert None to 0 for exponent columns and ensure float type
                    X = X.with_columns(pl.col(col).fill_null(0).cast(pl.Float64))
                else:
                    # Ensure all other columns are float and handle outliers
                    X = X.with_columns(pl.col(col).cast(pl.Float64))
                    # Calculate mean and std using Polars methods
                    mean = X.select(pl.col(col).mean()).item()
                    std = X.select(pl.col(col).std(ddof=1)).item()  # ddof=1 for sample standard deviation
                    
                    # Only clip if we have valid mean and std
                    if mean is not None and std is not None and std != 0:  # Also check for zero std
                        X = X.with_columns(
                            pl.col(col).clip(mean-3*std, mean+3*std)
                        )
                    else:
                        # If mean or std is None/zero, just fill nulls with 0
                        X = X.with_columns(
                            pl.col(col).fill_null(0)
                        )
            
            # Drop any rows with NaN values after conversion
            X = X.drop_nulls()
            y = y.drop_nulls()
            
            # For each step, only use data up to that step
            if step > 1:
                # Create a mask for valid rows
                valid_rows = features_df.filter(
                    # Include error-free cases
                    (pl.col('error_step') == 0) |
                    # Include cases where error occurs at or before this step
                    (pl.col('error_step') <= step)
                ).select('has_error').to_series()
                
                # Apply the mask to both X and y
                X = X.filter(pl.col('has_error').is_in(valid_rows))
                y = y.filter(pl.col('has_error').is_in(valid_rows))
            
            # Remove has_error from X before converting to numpy
            X = X.drop('has_error')
            
            # Get feature names before converting to numpy
            feature_names = list(X.columns)
            
            # Convert to numpy arrays for sklearn
            X_np = X.to_numpy()
            y_np = y.to_numpy().ravel()
            
            # Split data with fixed random state for consistency
            X_train, X_test, y_train, y_test = train_test_split(
                X_np, y_np, test_size=0.2, random_state=42, stratify=y_np
            )
            
            # Store validation data
            self.validation_data[step] = {
                'X': X_test,
                'y': y_test
            }
            
            # Set optimized model parameters
            params = {
                'objective': 'binary:logistic',
                'max_depth': 7,  # Balanced depth for complexity
                'learning_rate': 0.03,  # Balanced learning rate
                'eval_metric': 'auc',  # Use AUC for early stopping
                'subsample': 0.85,  # Balanced subsampling
                'colsample_bytree': 0.85,  # Balanced column sampling
                'min_child_weight': 2,  # Balanced minimum child weight
                'gamma': 0.5,  # Balanced minimum loss reduction
                'scale_pos_weight': len(y_train[y_train == 0]) / len(y_train[y_train == 1]),  # Handle class imbalance
                'tree_method': 'hist',  # Use histogram-based algorithm
                'grow_policy': 'lossguide',  # Grow trees based on loss reduction
                'max_leaves': 32,  # Allow moderate number of leaves
                'max_bin': 256,  # Good number of bins for discretization
                'reg_alpha': 0.5,  # L1 regularization
                'reg_lambda': 1.0,  # L2 regularization
                'n_estimators': 10000,  # Maximum number of boosting rounds
            }
            
            # Create and train XGBClassifier
            model = XGBClassifier(**params)
            
            # Train the model
            model.fit(
                X_train, y_train,
                eval_set=[(X_train, y_train), (X_test, y_test)],
                verbose=False
            )
            
            # Store model and calculate performance
            self.models[step] = model
            self.feature_importance[step] = dict(zip(feature_names, model.feature_importances_))
            
            # Calculate and store performance metrics
            predictions_prob = model.predict_proba(X_test)[:, 1]
            predictions = (predictions_prob > 0.5).astype(int)
            
            # Convert metrics to percentages
            self.performance[step] = {
                'roc_auc': roc_auc_score(y_test, predictions) * 100,
                'f1': f1_score(y_test, predictions, average='macro') * 100,
                'accuracy': accuracy_score(y_test, predictions) * 100,
                'confusion_matrix': confusion_matrix(y_test, predictions)
            }
            
    def describe(self):
        """Describe the model, including number of training data points and features."""
        description = {
            'num_steps': self.num_steps,
            'training_rows': self.stats['training_rows'],
            'error_free_pairs': self.stats['error_free_pairs'],
            'error_pairs': self.stats['error_pairs'],
            'models_trained': len(self.models)
        }
        
        if self.models:
            # Add average performance metrics across all steps
            avg_metrics = {
                'avg_roc_auc': np.mean([p['roc_auc'] for p in self.performance.values()]),
                'avg_f1': np.mean([p['f1'] for p in self.performance.values()]),
                'avg_accuracy': np.mean([p['accuracy'] for p in self.performance.values()])
            }
            description.update(avg_metrics)
            
            # Calculate uncaught error probability
            # This is the probability that all models fail to catch an error
            # For each step, we use (1 - accuracy) as the probability of missing an error
            # The total probability is the product of all individual probabilities
            error_miss_probabilities = [1 - p['accuracy'] for p in self.performance.values()]
            uncaught_error_probability = np.prod(error_miss_probabilities)
            description['uncaught_error_probability'] = uncaught_error_probability
            
            # Add step-wise performance metrics
            step_metrics = {}
            for step in range(1, self.num_steps + 1):
                if step in self.performance:
                    step_metrics[f'step_{step}'] = {
                        'accuracy': self.performance[step]['accuracy'],
                        'roc_auc': self.performance[step]['roc_auc'],
                        'f1_score': self.performance[step]['f1'],
                        'confusion_matrix': self.performance[step]['confusion_matrix'].tolist(),
                        'error_miss_probability': 1 - self.performance[step]['accuracy']  # Add individual error miss probability
                    }
            description['step_metrics'] = step_metrics
        
        return description

    def performance_metrics(self, step=None):
        """Return performance metrics for a specific step or all steps."""
        if step is not None:
            if step not in self.performance:
                raise ValueError(f"No model trained for step {step}")
            return self.performance[step]
        
        return self.performance

    def error_limit(self, step=None):
        """Calculate probability of divergence passing undetected through given step.
        
        For each step, calculates the probability that an error is not detected by any model
        up to and including that step. This is the product of (1 - accuracy) for each step.
        
        Args:
            step: The step to calculate up to. If None, uses the final step.
            
        Returns:
            float: Probability that an error passes undetected through all steps up to the given step.
        """
        if not self.models:
            raise ValueError("No models trained. Call train() first.")
            
        if step is None:
            step = self.num_steps
            
        if step not in self.models:
            raise ValueError(f"No model trained for step {step}")
            
        # Calculate probability of error passing undetected through each step
        # This is (1 - accuracy) for each step
        undetected_probs = []
        for s in range(1, step + 1):
            accuracy = self.performance[s]['accuracy']
            undetected_prob = 1 - accuracy
            undetected_probs.append(undetected_prob)
            
        # Calculate cumulative probability (product of individual probabilities)
        cumulative_prob = np.prod(undetected_probs)
        
        return cumulative_prob

    def _find_similar_errorless_run(self, prod_run, dev_dataset):
        """Find the most similar errorless run from dev dataset for a given prod run."""
        # Get errorless runs from dev dataset
        errorless_runs = dev_dataset.dataframe.filter(
            (pl.col('error_step') == 0) | 
            (pl.col('error_step').is_null())
        )
        
        if errorless_runs.is_empty():
            raise ValueError("No errorless runs found in dev dataset. Cannot find similar run for comparison.")
        
        # Calculate similarity scores
        similarities = []
        for dev_run in errorless_runs.iter_rows(named=True):
            # Calculate similarity between inputs
            similarity = embedding_model.similarity(
                embedding_model.encode([prod_run['input']], prompt_name='query'),
                embedding_model.encode([dev_run['input']], prompt_name='query')
            )[0][0].item()
            similarities.append((dev_run, similarity))
        
        # Return the run with highest similarity
        return max(similarities, key=lambda x: x[1])[0]

    def predict(self, dataset: Dataset, dev_dataset: Dataset, step: int = None) -> dict:
        """Perform inference on a new dataset using the trained models.
        
        Returns:
            Dictionary mapping run IDs to a dictionary of step predictions with probabilities
            Example: {
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
        """
        if not self.models:
            raise ValueError("No models trained. Call train() first.")
            
        if step is not None and step not in self.models:
            raise ValueError(f"No model trained for step {step}")
            
        # Determine which steps to predict for
        steps_to_predict = [step] if step is not None else range(1, self.num_steps + 1)
        
        # Initialize predictions dictionary
        predictions = {}
        
        # Process each prod run
        for prod_run in tqdm(dataset.dataframe.iter_rows(named=True), desc="Processing prod runs", total=len(dataset.dataframe)):
            run_id = str(prod_run['run_id'])
            predictions[run_id] = {}
            
            # Find most similar errorless run from dev dataset
            similar_run = self._find_similar_errorless_run(prod_run, dev_dataset)
            
            # Create path pair for prediction
            path_pair = {
                'run_id1': similar_run['run_id'],
                'run_id2': prod_run['run_id'],
                'input1': similar_run['input'],
                'input2': prod_run['input'],
                'path1': [str(similar_run[f'step{i}']) for i in range(1, self.num_steps + 1)],
                'path2': [str(prod_run[f'step{i}']) for i in range(1, self.num_steps + 1)],
                'has_error': False,  # We're comparing with an errorless run
                'error_step': 0
            }
            
            # Calculate metrics for this pair
            distances, exponents = process_paths(path_pair['path1'], path_pair['path2'])
            
            # Prepare features for prediction
            features = {
                'run_id1': path_pair['run_id1'],
                'run_id2': path_pair['run_id2'],
                'input1': path_pair['input1'],
                'input2': path_pair['input2'],
                'has_error': path_pair['has_error'],
                'error_step': path_pair['error_step'],
                'starting_distance': distances[0] if distances else None,
            }
            
            # Add distances and exponents
            for i in range(1, len(distances)):
                features[f'distance_{i}'] = distances[i]
            for i in range(1, len(exponents)):
                features[f'exponent_{i}'] = exponents[i]
            
            # Convert to DataFrame
            features_df = pl.DataFrame(features)
            
            # Calculate percent changes for distances
            for i in range(1, len(distances)):
                prev_col = f'distance_{i-1}' if i > 1 else 'starting_distance'
                curr_col = f'distance_{i}'
                features_df = features_df.with_columns([
                    (pl.when((pl.col(prev_col) != 0) & (pl.col(curr_col) != 0))
                     .then((pl.col(curr_col) - pl.col(prev_col)) / pl.col(prev_col) * 100)
                     .otherwise(None)
                     .alias(f'pct_change_distance_{i}'))
                ])
            
            # Calculate percent changes for exponents
            for i in range(1, len(exponents)):
                prev_col = f'exponent_{i-1}'
                curr_col = f'exponent_{i}'
                if prev_col in features_df.columns and curr_col in features_df.columns:
                    features_df = features_df.with_columns([
                        (pl.when(pl.col(prev_col).fill_null(0) != 0)
                         .then((pl.col(curr_col).fill_null(0) - pl.col(prev_col).fill_null(0)) / 
                               pl.col(prev_col).fill_null(0).replace(0, 1e-10) * 100)
                         .otherwise(0)
                         .alias(f'pct_change_exponent_{i}'))
                    ])
            
            # Handle infinite values
            float_cols = [col for col in features_df.columns if features_df[col].dtype in [pl.Float64, pl.Float32]]
            features_df = features_df.with_columns([
                pl.col(col).replace([float('inf'), float('-inf')], None) for col in float_cols
            ])
            
            # Drop rows with NA values only in the percent change columns
            pct_change_cols = [col for col in features_df.columns if 'pct_change' in col]
            features_df = features_df.drop_nulls(subset=pct_change_cols)
            
            # Make predictions for each step
            for s in steps_to_predict:
                # Prepare features for this step
                step_features = []
                step_features.append('starting_distance')
                
                # Add distances up to current step
                for i in range(1, s + 1):
                    if f'distance_{i}' in features_df.columns:
                        step_features.append(f'distance_{i}')
                
                # Add exponents up to current step
                for i in range(1, s + 1):
                    if f'exponent_{i}' in features_df.columns:
                        step_features.append(f'exponent_{i}')
                
                # Add distance percent changes up to current step
                for i in range(1, s + 1):
                    if f'pct_change_distance_{i}' in features_df.columns:
                        step_features.append(f'pct_change_distance_{i}')
                
                # Add exponent percent changes up to current step
                for i in range(1, s + 1):
                    if f'pct_change_exponent_{i}' in features_df.columns:
                        step_features.append(f'pct_change_exponent_{i}')
                
                # Prepare data for prediction
                X = features_df.select(step_features)
                
                # Convert data types and handle missing values
                for col in X.columns:
                    if col.startswith('exponent_'):
                        X = X.with_columns(pl.col(col).fill_null(0).cast(pl.Float64))
                    else:
                        X = X.with_columns(pl.col(col).cast(pl.Float64))
                        # Calculate mean and std using Polars methods
                        mean = X.select(pl.col(col).mean()).item()
                        std = X.select(pl.col(col).std(ddof=1)).item()  # ddof=1 for sample standard deviation
                        
                        # Only clip if we have valid mean and std
                        if mean is not None and std is not None and std != 0:  # Also check for zero std
                            X = X.with_columns(
                                pl.col(col).clip(mean-3*std, mean+3*std)
                            )
                        else:
                            # If mean or std is None/zero, just fill nulls with 0
                            X = X.with_columns(
                                pl.col(col).fill_null(0)
                            )
                
                # Convert to numpy arrays for prediction
                X_pred = X.to_numpy()
                
                # Get predictions
                probabilities = self.models[s].predict_proba(X_pred)[:, 1]
                predictions_binary = (probabilities > 0.5).astype(int)
                
                # Store results in the simplified format
                predictions[run_id][f'step_{s}'] = {
                    'prediction': bool(predictions_binary[0]),
                    'probability': float(probabilities[0])
                }
        
        return predictions

    def save_models(self, path: str):
        """Save trained models to disk.
        
        Args:
            path: Directory path to save models to
        """
        if not self.models:
            raise ValueError("No models trained. Call train() first.")
            
        import pickle
        
        # Generate a unique ID if not already set
        if self.model_id is None:
            self.model_id = str(uuid.uuid4())
            
        # Create a subdirectory for this model
        model_dir = os.path.join(path, self.model_id)
        os.makedirs(model_dir, exist_ok=True)
        
        # Save each model
        for step, model in self.models.items():
            model_path = os.path.join(model_dir, f'model_step_{step}.json')
            model.save_model(model_path)
        
        # Save metadata
        metadata = {
            'model_id': self.model_id,
            'num_steps': self.num_steps,
            'performance': self.performance,
            'feature_importance': self.feature_importance,
            'timestamp': str(datetime.datetime.now())
        }
        metadata_path = os.path.join(model_dir, 'metadata.pkl')
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)

    def load_models(self, path: str, model_id: str = None):
        """Load trained models from disk.
        
        Args:
            path: Directory path containing saved models
            model_id: Optional specific model ID to load. If None, loads the most recent model.
        """
        import pickle
        import glob
        
        if model_id is None:
            # Find the most recent model directory
            model_dirs = glob.glob(os.path.join(path, '*'))
            if not model_dirs:
                raise ValueError(f"No models found in {path}")
            model_dir = max(model_dirs, key=os.path.getctime)
            self.model_id = os.path.basename(model_dir)
        else:
            model_dir = os.path.join(path, model_id)
            if not os.path.exists(model_dir):
                raise ValueError(f"No model found with ID {model_id}")
            self.model_id = model_id
        
        # Load metadata
        metadata_path = os.path.join(model_dir, 'metadata.pkl')
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        
        self.num_steps = metadata['num_steps']
        self.performance = metadata['performance']
        self.feature_importance = metadata['feature_importance']
        
        # Load each model
        self.models = {}
        model_files = glob.glob(os.path.join(model_dir, 'model_step_*.json'))
        for model_file in model_files:
            step = int(os.path.basename(model_file).split('_')[-1].split('.')[0])
            model = XGBClassifier()
            model.load_model(model_file)
            self.models[step] = model

    def train_and_save(self, models_dir: str = 'models'):
        """Train the classifier and save the models."""
        self.train()
        os.makedirs(models_dir, exist_ok=True)
        self.save_models(models_dir)
        return {
            'model_id': self.model_id,
            'description': self.describe()
        }

    def load_and_predict(self, prod_dataset: Dataset, dev_dataset: Dataset, models_dir: str = 'models', model_id: str = None):
        """Load models and perform prediction on production data."""
        self.load_models(models_dir, model_id)
        return self.predict(prod_dataset, dev_dataset)

    def _generate_features(self, features_df: pl.DataFrame) -> pl.DataFrame:
        """Generate all features for the dataset.
        
        Args:
            features_df: DataFrame containing basic features (distances and exponents)
            
        Returns:
            DataFrame with all generated features
        """
        # Keep only the base features we need
        base_features = [
            'run_id1', 'run_id2', 'input1', 'input2', 'has_error', 'error_step',
            'starting_distance'
        ]
        
        # Add distances and exponents that exist in the DataFrame
        for i in range(1, 4):  # Check for steps 1, 2, 3
            if f'distance_{i}' in features_df.columns:
                base_features.append(f'distance_{i}')
            if f'exponent_{i}' in features_df.columns:
                base_features.append(f'exponent_{i}')
        
        features_df = features_df.select(base_features)
        
        # Calculate percent changes for distances
        for i in range(1, 4):  # Only for steps 1, 2, 3
            prev_col = f'distance_{i-1}' if i > 1 else 'starting_distance'
            curr_col = f'distance_{i}'
            if prev_col in features_df.columns and curr_col in features_df.columns:
                features_df = features_df.with_columns([
                    (pl.when((pl.col(prev_col) != 0) & (pl.col(curr_col) != 0))
                     .then((pl.col(curr_col) - pl.col(prev_col)) / pl.col(prev_col) * 100)
                     .otherwise(None)
                     .alias(f'pct_change_distance_{i}'))
                ])
        
        # Calculate percent changes for exponents
        for i in range(1, 4):  # Only for steps 1, 2, 3
            prev_col = f'exponent_{i-1}'
            curr_col = f'exponent_{i}'
            if prev_col in features_df.columns and curr_col in features_df.columns:
                features_df = features_df.with_columns([
                    (pl.when(pl.col(prev_col).fill_null(0) != 0)
                     .then((pl.col(curr_col).fill_null(0) - pl.col(prev_col).fill_null(0)) / 
                           pl.col(prev_col).fill_null(0).replace(0, 1e-10) * 100)
                     .otherwise(0)
                     .alias(f'pct_change_exponent_{i}'))
                ])
        
        # Handle infinite values
        float_cols = [col for col in features_df.columns if features_df[col].dtype in [pl.Float64, pl.Float32]]
        features_df = features_df.with_columns([
            pl.col(col).replace([float('inf'), float('-inf')], None) for col in float_cols
        ])
        
        # Drop rows with NA values only in the percent change columns
        pct_change_cols = [col for col in features_df.columns if 'pct_change' in col]
        features_df = features_df.drop_nulls(subset=pct_change_cols)
        
        return features_df

    def _prepare_step_features(self, features_df: pl.DataFrame, step: int) -> list:
        """Prepare features for a specific step.
        
        Args:
            features_df: DataFrame containing all generated features
            step: The step number to prepare features for
            
        Returns:
            List of feature names for this step
        """
        step_features = []
        
        # Add starting distance
        step_features.append('starting_distance')
        
        # Add distances up to current step
        for i in range(1, step + 1):
            if f'distance_{i}' in features_df.columns:
                step_features.append(f'distance_{i}')
        
        # Add exponents up to current step
        for i in range(1, step + 1):
            if f'exponent_{i}' in features_df.columns:
                step_features.append(f'exponent_{i}')
        
        # Add distance percent changes up to current step
        for i in range(1, step + 1):
            if f'pct_change_distance_{i}' in features_df.columns:
                step_features.append(f'pct_change_distance_{i}')
        
        # Add exponent percent changes up to current step
        for i in range(1, step + 1):
            if f'pct_change_exponent_{i}' in features_df.columns:
                step_features.append(f'pct_change_exponent_{i}')
        
        
        return step_features