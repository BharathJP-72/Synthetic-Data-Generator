"""
Core synthetic data generation engine.
Dynamic, modular, and independent system for generating synthetic data.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json
import logging
from concurrent.futures import ThreadPoolExecutor
import threading

from .schema_inference import SchemaInference
from .data_types import DataTypeManager
from ..generators.base_generator import BaseGenerator
from ..validators.data_validator import DataValidator
from ..utils.logger import get_logger
from ..utils.config import Config
from src.generators.file_generator import FileGenerator

logger = get_logger(__name__)


class SyntheticDataEngine:
    """
    Main engine for synthetic data generation.
    Supports both prompt-based and file-based generation.
    """
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.schema_inference = SchemaInference()
        self.data_type_manager = DataTypeManager()
        self.validator = DataValidator()
        self.generators: Dict[str, BaseGenerator] = {}
        self._lock = threading.Lock()
        self.register_generator("file", FileGenerator())  
        
        logger.info("SyntheticDataEngine initialized")
    
    def register_generator(self, name: str, generator: BaseGenerator) -> None:
        """Register a new generator."""
        with self._lock:
            self.generators[name] = generator
            logger.info(f"Generator '{name}' registered")
    
    def generate_from_prompt(
        self,
        prompt: str,
        num_rows: int = 1000,
        output_format: str = "pandas",
        **kwargs
    ) -> Union[pd.DataFrame, Dict[str, Any]]:
        """
        Generate synthetic data from natural language prompt.
        
        Args:
            prompt: Natural language description of desired data
            num_rows: Number of rows to generate
            output_format: Output format ('pandas', 'dict', 'json')
            **kwargs: Additional parameters
            
        Returns:
            Generated synthetic data
        """
        logger.info(f"Generating data from prompt: {prompt[:50]}...")
        
        # Parse prompt to extract schema
        schema = self.schema_inference.infer_from_field_list(prompt)
        
        # Generate data based on schema
        data = self._generate_from_schema(schema, num_rows, **kwargs)
        
        # Validate generated data
        validation_result = self.validator.validate_data(data, schema)
        if not validation_result.is_valid:
            logger.warning(f"Data validation failed: {validation_result.errors}")
        
        return self._format_output(data, output_format)
    
    def generate_from_file(
        self,
        file_path: str,
        num_rows: int = 1000,
        preserve_statistical_properties: bool = True,
        output_format: str = "pandas",
        **kwargs
    ) -> Union[pd.DataFrame, Dict[str, Any]]:
        """Generate synthetic data from existing file – preserves stats."""
        logger.info(f"Analysing file: {file_path}")
        original_df = self._load_file(file_path)

        if preserve_statistical_properties:
            schema = self.schema_inference.infer_from_data(original_df)
            data = self._generate_with_statistics(original_df, schema, num_rows)
        else:
            schema = self.schema_inference.infer_from_data(original_df)
            data = self._generate_from_schema(schema, num_rows, **kwargs)

        validation = self.validator.validate_data(data, schema)
        if not validation.is_valid:
            logger.warning(f"Validation issues: {validation.errors}")

        return self._format_output(data, output_format)
    
    def _generate_from_schema(self, schema: Dict[str, Any], num_rows: int, **kwargs) -> pd.DataFrame:
        """Always returns DataFrame – exporters handle conversion."""
        data = {}
        for column_name, column_spec in schema.items():
            generator_name = column_spec.get("generator", "default")
            if generator_name not in self.generators:
                generator_name = "mimesis"
            generator = self.generators[generator_name]
            data[column_name] = generator.generate(column_spec, num_rows, **kwargs)
        return pd.DataFrame(data)
    
    def _generate_with_statistics(self, original_df: pd.DataFrame, schema: Dict[str, Any], num_rows: int) -> pd.DataFrame:
        """Column-by-column statistical synthesis."""
        synthetic = {}
        for col_name, col_spec in schema.items():
            original_series = original_df[col_name]
            generator_name = col_spec.get("statistical_generator", "file")
            if generator_name in self.generators:
                generator = self.generators[generator_name]
                synthetic[col_name] = generator.generate(col_spec, num_rows, original_series=original_series)
            else:
                # fallback – sample with replacement
                synthetic[col_name] = original_series.sample(n=num_rows, replace=True).tolist()
        return pd.DataFrame(synthetic)
    
    def _generate_default_data(
        self,
        column_spec: Dict[str, Any],
        num_rows: int
    ) -> List[Any]:
        """Generate default data for column."""
        data_type = column_spec.get('type', 'string')
        
        if data_type == 'string':
            return [f"sample_{i}" for i in range(num_rows)]
        elif data_type == 'integer':
            return list(range(num_rows))
        elif data_type == 'float':
            return [float(i) for i in range(num_rows)]
        elif data_type == 'boolean':
            return [i % 2 == 0 for i in range(num_rows)]
        elif data_type == 'datetime':
            base_date = datetime.now()
            return [base_date.replace(day=(i % 28) + 1) for i in range(num_rows)]
        else:
            return [None] * num_rows
    
    def _generate_statistical_data(
        self,
        original_series: pd.Series,
        num_rows: int
    ) -> List[Any]:
        """Generate data preserving statistical properties."""
        if original_series.dtype == 'object':
            # Categorical data
            value_counts = original_series.value_counts(normalize=True)
            return np.random.choice(
                value_counts.index,
                size=num_rows,
                p=value_counts.values
            ).tolist()
        else:
            # Numerical data
            mean = original_series.mean()
            std = original_series.std()
            return np.random.normal(mean, std, num_rows).tolist()
    
    def _load_file(self, file_path: str) -> pd.DataFrame:
        """Load data from file."""
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith('.json'):
            return pd.read_json(file_path)
        elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            return pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
    
    # def _format_output(
    #     self,
    #     data: pd.DataFrame,
    #     output_format: str
    # ) -> Union[pd.DataFrame, Dict[str, Any]]:
    #     """Export helper – case-insensitive."""
    #     fmt = output_format.lower()
    #     if fmt == "pandas":
    #         return data
    #     if fmt == "dict":
    #         return data.to_dict("records")
    #     if fmt == "csv":
    #         return json.loads(data.to_json(orient="records"))   # keep dict for exporters
    #     if fmt == "json":
    #         return json.loads(data.to_json(orient="records"))
    #     raise ValueError(f"Unsupported output format: {output_format}")

    def _format_output(self, data: pd.DataFrame, output_format: str) -> pd.DataFrame:
        """Always return DataFrame – exporters will convert if needed."""
        return data