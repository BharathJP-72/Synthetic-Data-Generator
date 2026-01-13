"""
Data validation utilities for synthetic data.
"""
from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np

class ValidationResult:
    """Result of data validation."""
    
    def __init__(self, is_valid: bool = True, errors: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []

class DataValidator:
    """Validates generated synthetic data."""
    
    def __init__(self):
        self.validation_rules = {
            'integer': self._validate_integer,
            'float': self._validate_float,
            'string': self._validate_string,
            'boolean': self._validate_boolean,
            'datetime': self._validate_datetime,
            'categorical': self._validate_categorical
        }
    
    def validate_data(self, data: pd.DataFrame, schema: Dict[str, Any]) -> ValidationResult:
        """
        Validate generated data against schema.
        
        Args:
            data: Generated data DataFrame
            schema: Expected schema
            
        Returns:
            ValidationResult with status and errors
        """
        errors = []
        
        for column_name, column_spec in schema.items():
            if column_name not in data.columns:
                errors.append(f"Missing column: {column_name}")
                continue
            
            column_data = data[column_name]
            data_type = column_spec.get('type', 'string')
            
            # Validate data type
            if data_type in self.validation_rules:
                type_errors = self.validation_rules[data_type](column_data, column_spec)
                errors.extend(type_errors)
            
            # Validate constraints
            constraint_errors = self._validate_constraints(column_data, column_spec)
            errors.extend(constraint_errors)
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
    
    def _validate_integer(self, data: pd.Series, spec: Dict[str, Any]) -> List[str]:
        """Validate integer data."""
        errors = []
        
        try:
            # Check if all non-null values are integers
            non_null_data = data.dropna()
            if not non_null_data.apply(lambda x: isinstance(x, (int, np.integer))).all():
                errors.append(f"Column {data.name} contains non-integer values")
        except Exception as e:
            errors.append(f"Column {data.name} integer validation failed: {str(e)}")
        
        return errors
    
    def _validate_float(self, data: pd.Series, spec: Dict[str, Any]) -> List[str]:
        """Validate float data."""
        errors = []
        
        try:
            non_null_data = data.dropna()
            if not non_null_data.apply(lambda x: isinstance(x, (float, int, np.floating, np.integer))).all():
                errors.append(f"Column {data.name} contains non-numeric values")
        except Exception as e:
            errors.append(f"Column {data.name} float validation failed: {str(e)}")
        
        return errors
    
    def _validate_string(self, data: pd.Series, spec: Dict[str, Any]) -> List[str]:
        """Validate string data."""
        errors = []
        
        try:
            non_null_data = data.dropna()
            if not non_null_data.apply(lambda x: isinstance(x, str)).all():
                errors.append(f"Column {data.name} contains non-string values")
        except Exception as e:
            errors.append(f"Column {data.name} string validation failed: {str(e)}")
        
        return errors
    
    def _validate_boolean(self, data: pd.Series, spec: Dict[str, Any]) -> List[str]:
        """Validate boolean data."""
        errors = []
        
        try:
            non_null_data = data.dropna()
            if not non_null_data.apply(lambda x: isinstance(x, (bool, np.bool_))).all():
                errors.append(f"Column {data.name} contains non-boolean values")
        except Exception as e:
            errors.append(f"Column {data.name} boolean validation failed: {str(e)}")
        
        return errors
    
    def _validate_datetime(self, data: pd.Series, spec: Dict[str, Any]) -> List[str]:
        """Validate datetime data."""
        errors = []
        
        try:
            # Try to convert to datetime
            pd.to_datetime(data, errors='raise')
        except Exception as e:
            errors.append(f"Column {data.name} contains invalid datetime values: {str(e)}")
        
        return errors
    
    def _validate_categorical(self, data: pd.Series, spec: Dict[str, Any]) -> List[str]:
        """Validate categorical data."""
        errors = []
        
        try:
            # Check if all values are in allowed categories
            if 'categories' in spec:
                allowed = set(spec['categories'])
                unique_values = set(data.dropna().unique())
                invalid = unique_values - allowed
                if invalid:
                    errors.append(f"Column {data.name} contains invalid categories: {invalid}")
        except Exception as e:
            errors.append(f"Column {data.name} categorical validation failed: {str(e)}")
        
        return errors
    
    def _validate_constraints(self, data: pd.Series, spec: Dict[str, Any]) -> List[str]:
        """Validate column constraints."""
        errors = []
        constraints = spec.get('constraints', {})
        
        try:
            non_null_data = data.dropna()
            
            # Min/Max constraints
            if 'min' in constraints:
                min_val = constraints['min']
                if (non_null_data < min_val).any():
                    errors.append(f"Column {data.name} has values below minimum {min_val}")
            
            if 'max' in constraints:
                max_val = constraints['max']
                if (non_null_data > max_val).any():
                    errors.append(f"Column {data.name} has values above maximum {max_val}")
            
            # Length constraints (for strings)
            if 'length' in constraints and spec.get('type') == 'string':
                expected_length = constraints['length']
                if not non_null_data.apply(lambda x: len(str(x)) == expected_length).all():
                    errors.append(f"Column {data.name} has strings not matching length {expected_length}")
            
        except Exception as e:
            errors.append(f"Column {data.name} constraint validation failed: {str(e)}")
        
        return errors