"""
File-based generator – learns from real data and generates synthetic copy.
Preserves statistics (distributions, categories, ranges) automatically.
"""
import pandas as pd
import numpy as np
from typing import Any, Dict, List
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import LabelEncoder
import warnings

from .base_generator import BaseGenerator
from ..utils.logger import get_logger

logger = get_logger(__name__)

class FileGenerator(BaseGenerator):
    def __init__(self):
        super().__init__("file")

    def generate(self, column_spec: Dict[str, Any], num_rows: int, **kwargs) -> List[Any]:
        """Generate synthetic data preserving statistical properties of original file."""
        original_series = kwargs.get("original_series")
        if original_series is None:
            # fallback to basic generation
            return self._generate_basic(column_spec, num_rows)

        return self._generate_with_statistics(original_series, num_rows)

    def _generate_with_statistics(self, original_series: pd.Series, num_rows: int) -> List[Any]:
        """Preserve distribution & categories of original column."""
        dtype = str(original_series.dtype)

        if pd.api.types.is_numeric_dtype(original_series):
            return self._numeric_synthetic(original_series, num_rows)
        elif pd.api.types.is_categorical_dtype(original_series) or original_series.dtype == 'object':
            return self._categorical_synthetic(original_series, num_rows)
        elif pd.api.types.is_datetime64_any_dtype(original_series):
            return self._datetime_synthetic(original_series, num_rows)
        else:
            return original_series.sample(n=num_rows, replace=True).tolist()

    def _numeric_synthetic(self, series: pd.Series, num_rows: int) -> List[Any]:
        """Preserve numeric distribution using Gaussian Mixture."""
        valid = series.dropna()
        if len(valid) < 10:
            return self._numeric_fallback(series, num_rows)

        # Remove outliers for better fitting
        Q1, Q3 = valid.quantile(0.25), valid.quantile(0.75)
        IQR = Q3 - Q1
        filtered = valid[(valid >= Q1 - 1.5 * IQR) & (valid <= Q3 + 1.5 * IQR)]
        if len(filtered) < 10:
            filtered = valid

        # Fit Gaussian Mixture
        data_2d = filtered.values.reshape(-1, 1)
        best_gmm = None
        best_bic = float('inf')
        for n_comp in range(1, min(6, len(filtered))):
            try:
                gmm = GaussianMixture(n_components=n_comp, random_state=42)
                gmm.fit(data_2d)
                bic = gmm.bic(data_2d)
                if bic < best_bic:
                    best_bic = bic
                    best_gmm = gmm
            except Exception:
                continue

        if best_gmm is not None:
            samples, _ = best_gmm.sample(num_rows)
            generated = samples.flatten()
            # clamp to original range
            generated = np.clip(generated, valid.min(), valid.max())
            if series.dtype == 'int64':
                generated = np.round(generated).astype(int)
            return generated.tolist()

        # fallback
        return self._numeric_fallback(series, num_rows)

    def _categorical_synthetic(self, series: pd.Series, num_rows: int) -> List[Any]:
        """Preserve categorical distribution."""
        value_counts = series.value_counts(normalize=True)
        choices = value_counts.index.tolist()
        probabilities = value_counts.values.tolist()
        return np.random.choice(choices, size=num_rows, p=probabilities).tolist()

    def _datetime_synthetic(self, series: pd.Series, num_rows: int) -> List[Any]:
        """Preserve datetime distribution."""
        start_date = series.min()
        end_date = series.max()
        time_range = (end_date - start_date).total_seconds()
        random_seconds = np.random.uniform(0, time_range, num_rows)
        base_timestamps = start_date.value + (random_seconds * 1e9).astype(int)
        return pd.to_datetime(base_timestamps).strftime('%Y-%m-%d %H:%M:%S').tolist()

    def _generate_basic(self, column_spec: Dict[str, Any], num_rows: int) -> List[Any]:
        """Basic generation when no original series is provided."""
        data_type = column_spec.get('type', 'string')
        if data_type == 'string':
            return [f"sample_{i}" for i in range(num_rows)]
        elif data_type == 'integer':
            return list(range(num_rows))
        elif data_type == 'float':
            return [float(i) for i in range(num_rows)]
        elif data_type == 'boolean':
            return [i % 2 == 0 for i in range(num_rows)]
        else:
            return [None] * num_rows

    def _numeric_fallback(self, series: pd.Series, num_rows: int) -> List[Any]:
        """Fallback for numeric generation when Gaussian Mixture fails."""
        mean = series.mean()
        std = series.std()
        min_val = series.min()
        max_val = series.max()
        data = np.random.normal(mean, std, num_rows)
        data = np.clip(data, min_val, max_val)
        if series.dtype == 'int64':
            data = np.round(data).astype(int)
        return data.tolist()