"""
Aeryl SDK - A Python interface for Aeryl AI's Chaos Analysis Platform
"""

from .aeryl_model import AerylModel
from .dataset import Dataset
from .chaos_classifier import ChaosClassifier
from .metrics import process_paths

__version__ = "0.1.0"
__all__ = ['AerylModel', 'Dataset', 'ChaosClassifier', 'process_paths'] 