import polars as pl
from .metrics import process_paths
import numpy as np
from tqdm import tqdm
from typing import List, Dict, Any
import time
from datetime import datetime

class Dataset:
    """A class to handle dataset operations for chaos analysis."""
    
    def __init__(self, file: str):
        """Initialize the dataset from a CSV file.
        
        Args:
            file: Path to the CSV file containing the dataset
        """
        start_time = time.time()
        self.dataframe = pl.read_csv(file)
        
        # Create has_error column based on error_step
        self.dataframe = self.dataframe.with_columns([
            pl.when(pl.col('error_step') > 0)
            .then(True)
            .otherwise(False)
            .alias('has_error')
        ])
        
        self._initialize_steps()
        self._initialize_path_pairs()
        
    def _initialize_steps(self) -> None:
        """Initialize step-related attributes from the dataframe."""
        step_cols = [col for col in self.dataframe.columns if col.startswith('step')]
        self.num_steps = len(step_cols)
        self.step_cols = step_cols
        
    def _initialize_path_pairs(self) -> None:
        """Initialize path pairs from the dataframe."""
        error_free_paths = self._get_error_free_paths()
        error_paths = self._get_error_paths()
        self.path_pairs = self._create_path_pairs(error_free_paths, error_paths)
        
    def _get_error_free_paths(self) -> pl.DataFrame:
        """Get paths that are error-free (error_step is 0 or null)."""
        return self.dataframe.filter(
            (pl.col('error_step') == 0) | pl.col('error_step').is_null()
        )
        
    def _get_error_paths(self) -> pl.DataFrame:
        """Get paths that have errors (error_step > 0)."""
        return self.dataframe.filter(pl.col('error_step') > 0)
        
    def _create_path_pairs(self, error_free_paths: pl.DataFrame, 
                          error_paths: pl.DataFrame) -> List[Dict[str, Any]]:
        """Create path pairs from error-free and error paths."""
        path_pairs = []
        
        # Create pairs between error-free and error paths
        if not error_free_paths.is_empty() and not error_paths.is_empty():
            path_pairs.extend(self._create_error_pairs(error_free_paths, error_paths))
            
        # Create pairs between error-free paths
        if error_free_paths.height > 1:
            path_pairs.extend(self._create_error_free_pairs(error_free_paths))
            
        return path_pairs
        
    def _create_error_pairs(self, error_free_paths: pl.DataFrame, 
                           error_paths: pl.DataFrame) -> List[Dict[str, Any]]:
        """Create pairs between error-free and error paths."""
        # Create cross join with suffixes
        cross_join = error_free_paths.join(
            error_paths,
            how='cross',
            suffix='_2'
        )
        
        # Filter out same run_id and input
        cross_join = cross_join.filter(
            (pl.col('run_id') != pl.col('run_id_2')) & 
            (pl.col('input') != pl.col('input_2'))
        )
        
        return self._convert_to_path_pairs(cross_join, has_error=True)
        
    def _create_error_free_pairs(self, error_free_paths: pl.DataFrame) -> List[Dict[str, Any]]:
        """Create pairs between error-free paths."""
        # Create cross join with suffixes
        cross_join = error_free_paths.join(
            error_free_paths,
            how='cross',
            suffix='_2'
        )
        
        # Filter out same run_id, input and ensure run_id_1 < run_id_2
        cross_join = cross_join.filter(
            (pl.col('run_id') != pl.col('run_id_2')) & 
            (pl.col('input') != pl.col('input_2')) &
            (pl.col('run_id') < pl.col('run_id_2'))
        )
        
        return self._convert_to_path_pairs(cross_join, has_error=False)
        
    def _convert_to_path_pairs(self, df: pl.DataFrame, has_error: bool) -> List[Dict[str, Any]]:
        """Convert DataFrame rows to path pair dictionaries using vectorized operations."""
        # Pre-compute step columns for both paths
        path1_cols = self.step_cols
        path2_cols = [f'{col}_2' for col in self.step_cols]
        
        # Get all values as numpy arrays for faster processing
        path1_values = df.select(path1_cols).to_numpy()
        path2_values = df.select(path2_cols).to_numpy()
        run_ids = df.select(['run_id', 'run_id_2']).to_numpy()
        inputs = df.select(['input', 'input_2']).to_numpy()
        error_steps = df.select('error_step_2').to_numpy() if has_error else np.zeros((len(df), 1))
        
        # Vectorized string conversion
        path1_str = np.vectorize(str)(path1_values)
        path2_str = np.vectorize(str)(path2_values)
        
        # Create path pairs using list comprehension (faster than loop)
        return [
            {
                'run_id1': run_ids[i][0],
                'run_id2': run_ids[i][1],
                'input1': inputs[i][0],
                'input2': inputs[i][1],
                'path1': path1_str[i].tolist(),
                'path2': path2_str[i].tolist(),
                'has_error': has_error,
                'error_step': error_steps[i][0] if has_error else 0
            }
            for i in range(len(df))
        ]

    def create_candidate_paths(self) -> List[Dict[str, Any]]:
        """Create candidate path pairs for analysis."""
        error_free_paths = self._get_error_free_paths()
        error_paths = self._get_error_paths()
        return self._create_path_pairs(error_free_paths, error_paths)

    def calculate_metrics(self) -> pl.DataFrame:
        """Calculate metrics for path pairs using vectorized operations."""
        if not hasattr(self, 'path_pairs'):
            return self._create_empty_metrics_df()
            
        metrics_data = []
        for pair in tqdm(self.path_pairs, desc="Processing path pairs"):
            distances, exponents = process_paths(pair['path1'], pair['path2'])
            
            metrics = {
                'run_id1': pair['run_id1'],
                'run_id2': pair['run_id2'],
                'input1': pair['input1'],
                'input2': pair['input2'],
                'has_error': pair['has_error'],
                'error_step': pair['error_step'] or 0,
                'starting_distance': distances[0] if distances else None,
            }
            
            # Add distances and exponents
            for j in range(1, len(distances)):
                metrics[f'distance_{j}'] = distances[j]
            for j in range(1, len(exponents)):
                metrics[f'exponent_{j}'] = exponents[j]
                
            metrics_data.append(metrics)
            
        self.metrics_df = pl.DataFrame(metrics_data)
        return self.metrics_df
        
    def _create_empty_metrics_df(self) -> pl.DataFrame:
        """Create an empty metrics DataFrame with expected columns."""
        return pl.DataFrame({
            'run_id1': [],
            'run_id2': [],
            'input1': [],
            'input2': [],
            'has_error': [],
            'error_step': [],
            'starting_distance': []
        })

    def calculate_features(self) -> pl.DataFrame:
        """Calculate features from metrics."""
        if not hasattr(self, 'metrics_df'):
            raise ValueError("Must call calculate_metrics before calculate_features")
            
        features_df = self.metrics_df.clone()
        
        # Get column groups
        distance_cols = self._get_distance_columns(features_df)
        exponent_cols = self._get_exponent_columns(features_df)
        
        # Add features
        features_df = self._add_noise_features(features_df, distance_cols)
        features_df = self._add_ratio_features(features_df, distance_cols)
        features_df = self._add_exponential_features(features_df, distance_cols, exponent_cols)
        features_df = self._add_interaction_features(features_df, distance_cols, exponent_cols)
        features_df = self._add_percent_change_features(features_df, distance_cols, exponent_cols)
        features_df = self._cleanup_features(features_df)
        
        self.features_df = features_df
        return self.features_df
        
    def _get_distance_columns(self, df: pl.DataFrame) -> List[str]:
        """Get all distance-related columns."""
        return ['starting_distance'] + [col for col in df.columns if col.startswith('distance_')]
        
    def _get_exponent_columns(self, df: pl.DataFrame) -> List[str]:
        """Get all exponent-related columns."""
        return [col for col in df.columns if col.startswith('exponent_')]
        
    def _add_noise_features(self, df: pl.DataFrame, distance_cols: List[str]) -> pl.DataFrame:
        """Add noise to distance columns using vectorized operations."""
        noise_std = 0.0005
        # Generate all noise values at once
        noise_values = np.random.normal(0, noise_std, size=(len(df), len(distance_cols)))
        
        expressions = []
        for i, col in enumerate(distance_cols):
            expressions.append(
                pl.col(col).add(noise_values[:, i]).alias(f'{col}_noisy')
            )
        return df.with_columns(expressions)
            
    def _add_ratio_features(self, df: pl.DataFrame, distance_cols: List[str]) -> pl.DataFrame:
        """Add ratio features between distances and starting distance using vectorized operations."""
        expressions = []
        for i in range(1, len(distance_cols)):
            curr_col = distance_cols[i]
            if curr_col != 'starting_distance':
                # Regular ratio
                expressions.append(
                    (pl.col(curr_col) / pl.col('starting_distance')).alias(f'{curr_col}_ratio')
                )
                # Noisy ratio
                expressions.append(
                    (pl.col(f'{curr_col}_noisy') / pl.col('starting_distance_noisy')).alias(f'{curr_col}_noisy_ratio')
                )
        return df.with_columns(expressions)
        
    def _add_exponential_features(self, df: pl.DataFrame, 
                                distance_cols: List[str], 
                                exponent_cols: List[str]) -> pl.DataFrame:
        """Add exponential features for distances and exponents using vectorized operations."""
        expressions = []
        # Add all exponential features in one go
        for col in distance_cols:
            expressions.extend([
                pl.col(col).exp().alias(f'{col}_exp'),
                pl.col(f'{col}_noisy').exp().alias(f'{col}_noisy_exp')
            ])
            
        for col in exponent_cols:
            expressions.append(
                pl.col(col).fill_null(0).exp().alias(f'{col}_exp')
            )
        return df.with_columns(expressions)
            
    def _add_interaction_features(self, df: pl.DataFrame, 
                                distance_cols: List[str], 
                                exponent_cols: List[str]) -> pl.DataFrame:
        """Add interaction features between consecutive distances and exponents using vectorized operations."""
        expressions = []
        # Distance interactions
        for i in range(1, len(distance_cols)-1):
            curr_col = distance_cols[i]
            next_col = distance_cols[i+1]
            expressions.extend([
                (pl.col(curr_col) * pl.col(next_col)).alias(f'{curr_col}_{next_col}_interaction'),
                (pl.col(f'{curr_col}_noisy') * pl.col(f'{next_col}_noisy')).alias(f'{curr_col}_{next_col}_noisy_interaction')
            ])
            
        # Exponent interactions
        for i in range(1, len(exponent_cols)):
            curr_col = exponent_cols[i-1]
            next_col = exponent_cols[i]
            expressions.append(
                (pl.col(curr_col).fill_null(0) * pl.col(next_col).fill_null(0)).alias(f'{curr_col}_{next_col}_interaction')
            )
        return df.with_columns(expressions)
            
    def _add_percent_change_features(self, df: pl.DataFrame, 
                                   distance_cols: List[str], 
                                   exponent_cols: List[str]) -> pl.DataFrame:
        """Add percent change features for distances and exponents using vectorized operations."""
        expressions = []
        # Distance percent changes
        for i in range(1, len(distance_cols)):
            prev_col = distance_cols[i-1]
            curr_col = distance_cols[i]
            expressions.extend([
                ((pl.col(curr_col) - pl.col(prev_col)) / pl.col(prev_col) * 100).alias(f'distance_pct_change_{i}'),
                ((pl.col(f'{curr_col}_noisy') - pl.col(f'{prev_col}_noisy')) / 
                 pl.col(f'{prev_col}_noisy') * 100).alias(f'distance_noisy_pct_change_{i}')
            ])
            
        # Exponent percent changes
        for i in range(2, len(exponent_cols) + 1):
            prev_col = f'exponent_{i-1}'
            curr_col = f'exponent_{i}'
            expr = ((pl.col(curr_col).fill_null(0) - pl.col(prev_col).fill_null(0)) / 
                   pl.col(prev_col).fill_null(0).replace(0, 1e-10) * 100).alias(f'exponent_pct_change_{i}')
            expressions.append(expr)
            
        df = df.with_columns(expressions)
        
        # Replace infinite values with 0 in one operation
        pct_change_cols = [col for col in df.columns if 'pct_change' in col]
        inf_replacements = [pl.col(col).replace([float('inf'), float('-inf')], 0) for col in pct_change_cols]
        return df.with_columns(inf_replacements)
               
    def _cleanup_features(self, df: pl.DataFrame) -> pl.DataFrame:
        """Clean up features by handling infinite values and NA values using vectorized operations."""
        # Handle infinite values in one operation
        float_cols = [col for col in df.columns if df[col].dtype in [pl.Float64, pl.Float32]]
        inf_replacements = [pl.col(col).replace([float('inf'), float('-inf')], None) for col in float_cols]
        df = df.with_columns(inf_replacements)
                
        # Drop rows with NA values in percent change columns
        pct_change_cols = [col for col in df.columns if 'pct_change' in col]
        return df.drop_nulls(subset=pct_change_cols)

    def describe(self) -> Dict[str, Any]:
        """Describe the dataset statistics."""
        stats = {
            'num_runs': len(self.dataframe),
            'num_steps': self.num_steps,
            'error_free_runs': len(self._get_error_free_paths()),
            'error_runs': len(self._get_error_paths())
        }
        
        if hasattr(self, 'features_df'):
            stats.update({
                'training_rows': len(self.features_df),
                'unique_runs': len(set(self.features_df['run_id1'].unique()) | 
                                 set(self.features_df['run_id2'].unique())),
                'error_free_pairs': len(self.features_df.filter(~pl.col('has_error'))),
                'error_pairs': len(self.features_df.filter(pl.col('has_error')))
            })
        
        return stats

    def prepare_for_training(self) -> Dict[str, Any]:
        """Prepare dataset for training."""
        self.create_candidate_paths()
        self.calculate_metrics()
        self.calculate_features()
        return self.describe()

    def prepare_for_inference(self) -> Dict[str, Any]:
        """Prepare dataset for inference."""
        return {
            'num_runs': len(self.dataframe),
            'num_steps': self.num_steps
        }

if __name__ == '__main__':
    # Example usage
    dataset = Dataset('your_file.csv')
    metrics_df = dataset.calculate_metrics()
    features_df = dataset.calculate_features()
    print(f"Processed {len(metrics_df)} path pairs")