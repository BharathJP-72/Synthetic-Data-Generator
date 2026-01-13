"""
Quick test script to verify schema-based generation works.
"""
import sys
sys.path.insert(0, 'C:/Users/Dayanand S G/OneDrive/Desktop/synthetic-data-generator')

from src.core.engine import SyntheticDataEngine
from src.generators.mimesis_generator import MimesisGenerator
import json

# Initialize engine
engine = SyntheticDataEngine()
engine.register_generator("mimesis", MimesisGenerator())

# Test schema
schema = {
    "name": {"type": "string", "mimesis": "person.full_name", "generator": "mimesis"},
    "email": {"type": "string", "mimesis": "person.email", "generator": "mimesis"},
    "age": {"type": "integer", "mimesis": "person.age", "constraints": {"min": 25, "max": 60}, "generator": "mimesis"}
}

# Generate data
print("Generating data with schema...")
try:
    df = engine._generate_from_schema(schema, 10)
    print("\nSuccess! Generated data:")
    print(df)
    print("\nAge range check:")
    print(f"Min age: {df['age'].min()}")
    print(f"Max age: {df['age'].max()}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
