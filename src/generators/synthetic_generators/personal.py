"""
Personal data generators using Faker.
"""
from typing import Any, Dict, List
from faker import Faker
import random

from ..base_generator import BaseGenerator


class PersonalGenerator(BaseGenerator):
    """Generator for personal data."""
    
    def __init__(self):
        super().__init__("personal")
        self.faker = Faker()
    
    def generate(
        self,
        column_spec: Dict[str, Any],
        num_rows: int,
        **kwargs
    ) -> List[Any]:
        """Generate personal data."""
        sub_type = column_spec.get('sub_type', 'name')
        
        if sub_type == 'name':
            return self._generate_name(column_spec, num_rows, **kwargs)
        elif sub_type == 'email':
            return self._generate_email(column_spec, num_rows, **kwargs)
        elif sub_type == 'phone':
            return self._generate_phone(column_spec, num_rows, **kwargs)
        elif sub_type == 'age':
            return self._generate_age(column_spec, num_rows, **kwargs)
        elif sub_type == 'ssn':
            return self._generate_ssn(column_spec, num_rows, **kwargs)
        else:
            return [self.faker.name() for _ in range(num_rows)]
    
    def _generate_name(self, column_spec: Dict[str, Any], num_rows: int, **kwargs) -> List[str]:
        """Generate names."""
        name_type = kwargs.get('name_type', 'full')
        
        if name_type == 'first':
            return [self.faker.first_name() for _ in range(num_rows)]
        elif name_type == 'last':
            return [self.faker.last_name() for _ in range(num_rows)]
        else:
            return [self.faker.name() for _ in range(num_rows)]
    
    def _generate_email(self, column_spec: Dict[str, Any], num_rows: int, **kwargs) -> List[str]:
        """Generate email addresses."""
        domain = kwargs.get('domain')
        
        if domain:
            return [f"{self.faker.user_name()}@{domain}" for _ in range(num_rows)]
        else:
            return [self.faker.email() for _ in range(num_rows)]
    
    def _generate_phone(self, column_spec: Dict[str, Any], num_rows: int, **kwargs) -> List[str]:
        """Generate phone numbers."""
        format_pattern = kwargs.get('format', '###-###-####')
        return [self.faker.numerify(format_pattern) for _ in range(num_rows)]
    
    def _generate_age(self, column_spec: Dict[str, Any], num_rows: int, **kwargs) -> List[int]:
        """Generate ages."""
        constraints = column_spec.get('constraints', {})
        min_age = constraints.get('min', 18)
        max_age = constraints.get('max', 90)
        
        return [random.randint(min_age, max_age) for _ in range(num_rows)]
    
    def _generate_ssn(self, column_spec: Dict[str, Any], num_rows: int, **kwargs) -> List[str]:
        """Generate SSNs."""
        return [self.faker.ssn() for _ in range(num_rows)]