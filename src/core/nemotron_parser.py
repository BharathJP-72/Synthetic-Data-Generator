"""
NVIDIA Nemotron-based prompt parser for intelligent field extraction.
Uses Nemotron LLM to understand natural language prompts and extract field specifications.
"""
import os
import json
from typing import Dict, Any, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

from ..utils.logger import get_logger

# Load environment variables from .env file
load_dotenv()

logger = get_logger(__name__)


class NemotronPromptParser:
    """Parse natural language prompts using NVIDIA Nemotron model."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Nemotron parser.
        
        Args:
            api_key: NVIDIA API key. If None, reads from NVIDIA_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY")
        self.client = None
        self.enabled = False
        
        if self.api_key:
            try:
                self.client = OpenAI(
                    base_url="https://integrate.api.nvidia.com/v1",
                    api_key=self.api_key
                )
                self.enabled = True
                logger.info("Nemotron parser initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Nemotron: {e}. Falling back to regex parsing.")
                self.enabled = False
        else:
            logger.info("NVIDIA_API_KEY not found. Nemotron parser disabled. Using regex fallback.")
    
    def parse_prompt(self, prompt: str) -> List[Dict[str, Any]]:
        """
        Parse a natural language prompt to extract field specifications.
        
        Args:
            prompt: Natural language description of desired data
            
        Returns:
            List of field specifications with name, type, and constraints
        """
        if not self.enabled:
            return self._fallback_parse(prompt)
        
        try:
            # Create a structured prompt for Nemotron
            system_prompt = """You are an expert data schema designer. Your task is to analyze natural language descriptions of data and extract structured field specifications.

For each field mentioned in the prompt, identify:
1. Field name (clean, snake_case)
2. Data type (string, integer, float, datetime, boolean)
3. Mimesis provider OR custom provider
4. Constraints (min, max, start, end if mentioned)

CRITICAL MAPPING RULES (follow these EXACTLY):

DEPARTMENTS/DIVISIONS:
- "department" or "division" → use custom.department (NOT person.occupation)
- Examples: Sales, Marketing, Engineering, HR, Finance

PRODUCTS:
- "product name" or "product" → use custom.product (NOT food.dish)
- Examples: Laptop, Mouse, Keyboard, Monitor

COMPANIES:
- "company" or "organization" → use custom.company (NOT person names)
- Examples: TechCorp Solutions, Global Innovations Inc

STATUS/STATE:
- "status" or "state" → use custom.status
- Examples: Active, Pending, Completed

PERSON DATA:
- "employee name" or "customer name" → use person.full_name
- "email" → use person.email
- "phone" → use person.telephone
- "age" → use person.age with appropriate constraints

FINANCIAL:
- "salary" → use finance.price with constraints like min:30000, max:200000
- "price" → use finance.price with constraints like min:10, max:1000

DATES:
- "joining date" or "hire date" or "order date" → use datetime.date
- Constraints: start:2020, end:2024

IDs:
- "employee id" or "customer id" → use person.identifier

Return ONLY a JSON array of field objects. No explanations."""

            user_prompt = f"""Extract field specifications from this prompt:
"{prompt}"

Return JSON array like:
[
  {{"name": "employee_names", "type": "string", "mimesis": "person.full_name"}},
  {{"name": "employee_ages", "type": "integer", "mimesis": "person.age", "constraints": {{"min": 22, "max": 65}}}},
  {{"name": "departments", "type": "string", "provider": "custom.department"}},
  {{"name": "salaries", "type": "float", "mimesis": "finance.price", "constraints": {{"min": 30000, "max": 200000}}}},
  {{"name": "joining_dates", "type": "datetime", "mimesis": "datetime.date", "constraints": {{"start": 2020, "end": 2024}}}}
]

Use "provider": "custom.department" for departments.
Use "provider": "custom.product" for product names.
Use "provider": "custom.company" for company names.
Use "provider": "custom.status" for status fields."""

            # Call Nemotron API
            completion = self.client.chat.completions.create(
                model="meta/llama-3.1-70b-instruct",  # Updated model name for NVIDIA API
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,  # Low temperature for consistent output
                max_tokens=1024
            )
            
            # Extract and parse response
            response_text = completion.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            # Parse JSON
            fields = json.loads(response_text)
            
            logger.info(f"Nemotron extracted {len(fields)} fields from prompt")
            return fields
            
        except Exception as e:
            logger.warning(f"Nemotron parsing failed: {e}. Falling back to regex.")
            return self._fallback_parse(prompt)
    
    def _fallback_parse(self, prompt: str) -> List[Dict[str, Any]]:
        """
        Fallback regex-based parsing when Nemotron is unavailable.
        
        Args:
            prompt: Natural language prompt
            
        Returns:
            List of field specifications
        """
        import re
        
        # Remove common descriptive phrases
        cleaned = prompt.lower()
        for phrase in ["including", "with", "containing", "data for", "generate", "create", "records for", "online orders"]:
            cleaned = cleaned.replace(phrase, "")
        
        # Split by common delimiters
        fields = []
        parts = cleaned.split(" and ")
        for part in parts:
            subparts = part.split(",")
            fields.extend(subparts)
        
        # Clean and parse each field
        result = []
        for field in fields:
            field = field.strip()
            if not field or len(field) < 2:
                continue
            
            # Create field spec
            spec = self._infer_field_spec(field)
            if spec:
                result.append(spec)
        
        return result
    
    def _infer_field_spec(self, field: str) -> Optional[Dict[str, Any]]:
        """Infer field specification from field name using regex patterns."""
        field_lower = field.lower()
        
        # Clean field name
        words = field_lower.split()
        filtered_words = [w for w in words if w not in ["the", "a", "an", "of", "for", "in", "on", "at"]]
        clean_name = "_".join(filtered_words)
        clean_name = clean_name.replace(" ", "_")
        import re
        clean_name = re.sub(r'\W+', '_', clean_name).strip('_')
        
        if not clean_name:
            return None
        
        spec = {"name": clean_name, "type": "string"}
        
        # Priority-based matching - check specific patterns first
        if "product" in field_lower and ("name" in field_lower or "names" in field_lower):
            spec["mimesis"] = "food.dish"
        elif "quantit" in field_lower or field_lower in ["qty", "count", "units"]:
            spec["type"] = "integer"
            spec["mimesis"] = "person.age"
            spec["constraints"] = {"min": 1, "max": 100}
        elif "customer" in field_lower and "id" in field_lower:
            spec["mimesis"] = "person.identifier"
        elif "order" in field_lower and "id" in field_lower:
            spec["mimesis"] = "person.identifier"
        elif "price" in field_lower or "cost" in field_lower:
            spec["type"] = "float"
            spec["mimesis"] = "finance.price"
            spec["constraints"] = {"min": 10, "max": 1000}
        elif "timestamp" in field_lower or ("order" in field_lower and "date" in field_lower):
            spec["type"] = "datetime"
            spec["mimesis"] = "datetime.date"
            spec["constraints"] = {"start": 2020, "end": 2024}
        elif "customer" in field_lower and "name" in field_lower:
            spec["mimesis"] = "person.full_name"
        elif "email" in field_lower:
            spec["mimesis"] = "person.email"
        elif "phone" in field_lower or "telephone" in field_lower:
            spec["mimesis"] = "person.telephone"
        elif "address" in field_lower:
            spec["mimesis"] = "address.address"
        elif "city" in field_lower:
            spec["mimesis"] = "address.city"
        elif "id" in field_lower or "identifier" in field_lower:
            spec["mimesis"] = "person.identifier"
        elif "date" in field_lower or "time" in field_lower:
            spec["type"] = "datetime"
            spec["mimesis"] = "datetime.date"
            spec["constraints"] = {"start": 2020, "end": 2024}
        else:
            # Default fallback
            spec["mimesis"] = "person.full_name"
        
        return spec
