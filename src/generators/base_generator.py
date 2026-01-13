"""
Base generator class for synthetic data generation.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List
import pandas as pd
import numpy as np

from ..utils.logger import get_logger

logger = get_logger(__name__)


class BaseGenerator(ABC):
    """Base class for all data generators."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logger
    
    @abstractmethod
    def generate(
        self,
        column_spec: Dict[str, Any],
        num_rows: int,
        **kwargs
    ) -> List[Any]:
        """
        Generate synthetic data based on column specification.
        
        Args:
            column_spec: Column specification dictionary
            num_rows: Number of rows to generate
            **kwargs: Additional parameters
            
        Returns:
            List of generated values
        """
        pass
    
    def generate_with_statistics(
        self,
        column_spec: Dict[str, Any],
        original_series: pd.Series,
        num_rows: int
    ) -> List[Any]:
        """
        Generate data preserving statistical properties.
        
        Args:
            column_spec: Column specification
            original_series: Original data series
            num_rows: Number of rows to generate
            
        Returns:
            List of generated values
        """
        # Default implementation - override in subclasses
        return self.generate(column_spec, num_rows)
    
    def validate_column_spec(self, column_spec: Dict[str, Any]) -> bool:
        """
        Validate column specification.
        
        Args:
            column_spec: Column specification
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['type']
        return all(field in column_spec for field in required_fields)