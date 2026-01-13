"""
Prompt-based generator using NLP to understand data requirements.
"""
from typing import Any, Dict, List
import random
import re
from faker import Faker

from .base_generator import BaseGenerator
from ..utils.logger import get_logger

logger = get_logger(__name__)


class PromptGenerator(BaseGenerator):
    """Generator that understands natural language prompts."""
    
    def __init__(self):
        super().__init__("prompt")
        self.faker = Faker()
        self.generators = {
            'name': self._generate_name,
            'email': self._generate_email,
            'phone': self._generate_phone,
            'address': self._generate_address,
            'company': self._generate_company,
            'job': self._generate_job,
            'date': self._generate_date,
            'number': self._generate_number,
            'text': self._generate_text,
            'boolean': self._generate_boolean,
            'choice': self._generate_choice
        }
    
    def generate(
        self,
        column_spec: Dict[str, Any],
        num_rows: int,
        **kwargs
    ) -> List[Any]:
        """
        Generate data based on prompt specification.
        
        Args:
            column_spec: Column specification
            num_rows: Number of rows to generate
            **kwargs: Additional parameters
            
        Returns:
            List of generated values
        """
        prompt = column_spec.get('prompt', '')
        data_type = column_spec.get('type', 'string')
        
        # Determine generator based on prompt content
        generator_type = self._determine_generator_type(prompt, data_type)
        
        if generator_type in self.generators:
            return self.generators[generator_type](column_spec, num_rows, **kwargs)
        else:
            return self._generate_default(column_spec, num_rows, **kwargs)
    
    def _determine_generator_type(self, prompt: str, data_type: str) -> str:
        """Determine generator type from prompt and data type."""
        prompt_lower = prompt.lower()
        
        if 'name' in prompt_lower:
            return 'name'
        elif 'email' in prompt_lower:
            return 'email'
        elif 'phone' in prompt_lower:
            return 'phone'
        elif 'address' in prompt_lower:
            return 'address'
        elif 'company' in prompt_lower:
            return 'company'
        elif 'job' in prompt_lower or 'title' in prompt_lower:
            return 'job'
        elif 'date' in prompt_lower or 'time' in prompt_lower:
            return 'date'
        elif data_type == 'boolean':
            return 'boolean'
        elif data_type in ['integer', 'float']:
            return 'number'
        elif 'choice' in prompt_lower or 'select' in prompt_lower:
            return 'choice'
        else:
            return 'text'
    
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
        domain = kwargs.get('domain', None)
        
        if domain:
            return [f"{self.faker.user_name()}@{domain}" for _ in range(num_rows)]
        else:
            return [self.faker.email() for _ in range(num_rows)]
    
    def _generate_phone(self, column_spec: Dict[str, Any], num_rows: int, **kwargs) -> List[str]:
        """Generate phone numbers."""
        format_pattern = kwargs.get('format', '###-###-####')
        return [self.faker.numerify(format_pattern) for _ in range(num_rows)]
    
    def _generate_address(self, column_spec: Dict[str, Any], num_rows: int, **kwargs) -> List[str]:
        """Generate addresses."""
        address_type = kwargs.get('address_type', 'full')
        
        if address_type == 'street':
            return [self.faker.street_address() for _ in range(num_rows)]
        elif address_type == 'city':
            return [self.faker.city() for _ in range(num_rows)]
        elif address_type == 'state':
            return [self.faker.state() for _ in range(num_rows)]
        else:
            return [self.faker.address() for _ in range(num_rows)]
    
    def _generate_company(self, column_spec: Dict[str, Any], num_rows: int, **kwargs) -> List[str]:
        """Generate company names."""
        return [self.faker.company() for _ in range(num_rows)]
    
    def _generate_job(self, column_spec: Dict[str, Any], num_rows: int, **kwargs) -> List[str]:
        """Generate job titles."""
        return [self.faker.job() for _ in range(num_rows)]
    
    def _generate_date(self, column_spec: Dict[str, Any], num_rows: int, **kwargs) -> List[str]:
        """Generate dates."""
        date_format = kwargs.get('date_format', '%Y-%m-%d')
        start_date = kwargs.get('start_date', '-30y')
        end_date = kwargs.get('end_date', 'today')
        
        dates = []
        for _ in range(num_rows):
            date_obj = self.faker.date_between(start_date=start_date, end_date=end_date)
            dates.append(date_obj.strftime(date_format))
        
        return dates
    
    def _generate_number(self, column_spec: Dict[str, Any], num_rows: int, **kwargs) -> List[Any]:
        """Generate numbers."""
        constraints = column_spec.get('constraints', {})
        min_val = constraints.get('min', 0)
        max_val = constraints.get('max', 100)
        
        if column_spec.get('type') == 'integer':
            return [random.randint(min_val, max_val) for _ in range(num_rows)]
        else:
            return [random.uniform(min_val, max_val) for _ in range(num_rows)]
    
    def _generate_text(self, column_spec: Dict[str, Any], num_rows: int, **kwargs) -> List[str]:
        """Generate text."""
        length = kwargs.get('length', 100)
        return [self.faker.text(max_nb_chars=length) for _ in range(num_rows)]
    
    def _generate_boolean(self, column_spec: Dict[str, Any], num_rows: int, **kwargs) -> List[bool]:
        """Generate boolean values."""
        probability = kwargs.get('probability', 0.5)
        return [random.random() < probability for _ in range(num_rows)]
    
    def _generate_choice(self, column_spec: Dict[str, Any], num_rows: int, **kwargs) -> List[str]:
        """Generate choices from predefined options."""
        choices = kwargs.get('choices', ['Option A', 'Option B', 'Option C'])
        return [random.choice(choices) for _ in range(num_rows)]
    
    def _generate_default(self, column_spec: Dict[str, Any], num_rows: int, **kwargs) -> List[Any]:
        """Generate default data."""
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