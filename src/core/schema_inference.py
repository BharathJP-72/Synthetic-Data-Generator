"""
Dynamic schema inference from various inputs.
Now powered by NVIDIA Nemotron for intelligent prompt understanding.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Union
import json
import re
from datetime import datetime

from ..utils.logger import get_logger
from .nemotron_parser import NemotronPromptParser

logger = get_logger(__name__)


class SchemaInference:
    """Infer schema from different input sources."""
    
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
        # Initialize Nemotron parser
        self.nemotron = NemotronPromptParser()
    
    def infer_from_field_list(self, prompt: str) -> Dict[str, Any]:
        """
        Parse natural language prompt using Nemotron LLM or regex fallback.
        
        Args:
            prompt: Natural language description of desired data
            
        Returns:
            Schema dictionary mapping field names to specifications
        """
        logger.info(f"Parsing prompt with Nemotron: {prompt[:100]}...")
        
        # Use Nemotron to parse the prompt
        fields = self.nemotron.parse_prompt(prompt)
        
        # Convert to schema format
        schema = {}
        for field_spec in fields:
            field_name = field_spec.get("name", "field")
            schema[field_name] = {
                "type": field_spec.get("type", "string")
            }
            
            # Handle both mimesis and custom providers
            if "provider" in field_spec:
                # Custom provider (e.g., custom.department)
                schema[field_name]["provider"] = field_spec["provider"]
            elif "mimesis" in field_spec:
                # Mimesis provider (e.g., person.full_name)
                schema[field_name]["mimesis"] = field_spec["mimesis"]
            else:
                # Default fallback
                schema[field_name]["mimesis"] = "person.full_name"
            
            # Add constraints if present
            if "constraints" in field_spec:
                schema[field_name]["constraints"] = field_spec["constraints"]
        
        logger.info(f"Generated schema with {len(schema)} fields")
        return schema
    
    def infer_from_data(self, data: Union[pd.DataFrame, Dict[str, Any]]) -> Dict[str, Any]:
        """Infer schema from existing data."""
        logger.info("Inferring schema from data")
        
        if isinstance(data, dict):
            data = pd.DataFrame(data)
        
        schema = {}
        for column in data.columns:
            schema[column] = self._analyze_column(data[column])
        
        return schema
    
    def _analyze_column(self, series: pd.Series) -> Dict[str, Any]:
        """Analyze pandas series to determine schema."""
        spec = {
            'type': self._pandas_dtype_to_string(series.dtype),
            'generator': 'statistical',
            'constraints': {},
            'statistics': {}
        }
        
        # Basic statistics
        spec['statistics']['count'] = int(series.count())
        spec['statistics']['null_count'] = int(series.isnull().sum())
        spec['statistics']['null_percentage'] = float(series.isnull().mean())
        
        if pd.api.types.is_numeric_dtype(series):
            spec['statistics'].update({
                'mean': float(series.mean()),
                'std': float(series.std()),
                'min': float(series.min()),
                'max': float(series.max()),
                'median': float(series.median())
            })
        elif pd.api.types.is_categorical_dtype(series) or series.dtype == 'object':
            value_counts = series.value_counts()
            spec['statistics']['unique_count'] = int(series.nunique())
            spec['statistics']['top_values'] = value_counts.head(10).to_dict()
        
        return spec
    
    def _pandas_dtype_to_string(self, dtype) -> str:
        """Convert pandas dtype to string type."""
        dtype_str = str(dtype)
        
        for pandas_type, string_type in self.type_mapping.items():
            if pandas_type in dtype_str:
                return string_type
        
        return 'string'