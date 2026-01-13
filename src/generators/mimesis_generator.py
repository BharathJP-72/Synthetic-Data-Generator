"""
Bullet-proof Mimesis generator – version-agnostic.
Maps "product" → realistic items, not people.
"""
from typing import Any, Dict, List
import random
from .base_generator import BaseGenerator

# ----------- import only what exists -----------
_PROV: Dict[str, Any] = {}

"""
Mimesis-based data generator with custom provider support.
"""
import random
from mimesis import Person, Address, Finance, Datetime, Payment, Food, Internet
from typing import Dict, Any, List

from ..utils.logger import get_logger
from .custom_providers import CustomProviders

logger = get_logger(__name__)

# Initialize Mimesis providers
_PROV = {
    "person": Person(),
    "address": Address(),
    "finance": Finance(),
    "datetime": Datetime(),
    "payment": Payment(),
    "food": Food(),
    "internet": Internet()
}

# Initialize custom providers
_CUSTOM = CustomProviders()


class MimesisGenerator:
    """Generate data using Mimesis library with custom provider support."""
    
    def generate(self, column_spec: Dict[str, Any], num_rows: int, **kwargs) -> List[Any]:
        """
        Generate data based on column specification.
        
        Args:
            column_spec: Column specification with provider info
            num_rows: Number of rows to generate
            
        Returns:
            List of generated values
        """
        # Check if it's a custom provider
        if "provider" in column_spec:
            provider_path = column_spec["provider"]
            if provider_path.startswith("custom."):
                # Custom provider
                provider_func = provider_path.split(".", 1)[1]
                return [getattr(_CUSTOM, provider_func)() for _ in range(num_rows)]
        
        # Mimesis provider
        method = column_spec.get("mimesis", "person.full_name")
        provider, func = method.split(".", 1)
        func = {"phone": "telephone", "cell": "telephone", "mobile": "telephone"}.get(func, func)

        # Fail-safe provider
        if provider not in _PROV:
            provider = {
                "business": "person",
                "food": "food",
            }.get(provider, "person")
            func = {"commerce_sector": "full_name",
                    "company": "full_name",
                    "dish": "dish"}.get(func, "full_name")

        prov_obj = _PROV[provider]

        # Generate data
        rows = []
        for _ in range(num_rows):
            if method == "person.age":
                c = column_spec.get("constraints", {})
                rows.append(random.randint(c.get("min", 18), c.get("max", 65)))
            elif method == "finance.price":
                c = column_spec.get("constraints", {})
                rows.append(prov_obj.price(c.get("min", 10), c.get("max", 500)))
            elif method == "datetime.date":
                c = column_spec.get("constraints", {})
                start = c.get("start", 2020)
                end   = c.get("end", 2024)
                rows.append(prov_obj.date(start=start, end=end).strftime("%Y-%m-%d"))
            else:
                rows.append(getattr(prov_obj, func)())
        return rows