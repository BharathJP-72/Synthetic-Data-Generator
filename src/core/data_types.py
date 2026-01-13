"""
Data type manager for synthetic data generation.
Handles type inference, validation, and conversion.
"""
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime

class DataTypeManager:
    """Manages data type inference and conversion."""
    
    def __init__(self):
        self.type_mapping = {
            'int64': 'integer',
            'float64': 'float',
            'object': 'string',
            'bool': 'boolean',
            'datetime64': 'datetime',
            'timedelta64': 'timedelta',
            'category': 'categorical'
        }
    
    def infer_type(self, data: pd.Series) -> str:
        """Infer data type from pandas series."""
        dtype = str(data.dtype)
        
        for pandas_type, string_type in self.type_mapping.items():
            if pandas_type in dtype:
                return string_type
        
        return 'string'
    
    def convert_type(self, data: List[Any], target_type: str) -> List[Any]:
        """Convert data to target type."""
        if target_type == 'integer':
            return [int(x) if pd.notnull(x) else None for x in data]
        elif target_type == 'float':
            return [float(x) if pd.notnull(x) else None for x in data]
        elif target_type == 'boolean':
            return [bool(x) if pd.notnull(x) else None for x in data]
        elif target_type == 'datetime':
            return [pd.to_datetime(x) if pd.notnull(x) else None for x in data]
        else:
            return [str(x) if pd.notnull(x) else None for x in data]
    
    def get_generator_hint(self, data_type: str) -> str:
        """Get generator hint for data type."""
        hints = {
            'integer': 'default.integer',
            'float': 'default.float',
            'string': 'default.string',
            'boolean': 'default.boolean',
            'datetime': 'default.datetime',
            'categorical': 'default.categorical'
        }
        return hints.get(data_type, 'default.string')