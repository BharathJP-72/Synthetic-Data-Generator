"""
Test the improved prompt-based generator with various prompts.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.engine import SyntheticDataEngine
from src.generators.mimesis_generator import MimesisGenerator

def test_prompt_generation():
    """Test various prompts to ensure realistic data generation."""
    
    # Initialize engine
    engine = SyntheticDataEngine()
    engine.register_generator("mimesis", MimesisGenerator())
    
    test_cases = [
        {
            "name": "Online Orders",
            "prompt": "online orders including customer IDs, product names, quantities, prices, order timestamps",
            "rows": 10
        },
        {
            "name": "Employee Data",
            "prompt": "employee name, email, department, salary 40000-120000, hire date 2020-2024, age 22-65",
            "rows": 10
        },
        {
            "name": "E-commerce Products",
            "prompt": "product name, SKU, price $10-$500, quantity 1-100, category, brand",
            "rows": 10
        },
        {
            "name": "Customer Records",
            "prompt": "customer name, email, phone, address, city, state, zip code, age 18-75",
            "rows": 10
        },
        {
            "name": "Financial Transactions",
            "prompt": "transaction ID, customer name, amount $50-$5000, date 2023-2024, status",
            "rows": 10
        }
    ]
    
    print("=" * 80)
    print("TESTING IMPROVED PROMPT-BASED GENERATOR")
    print("=" * 80)
    
    for test in test_cases:
        print(f"\n\n{'='*80}")
        print(f"TEST: {test['name']}")
        print(f"PROMPT: {test['prompt']}")
        print(f"{'='*80}\n")
        
        try:
            # Generate data
            df = engine.generate_from_prompt(test['prompt'], test['rows'])
            
            # Display results
            print(df.to_string())
            print(f"\n✅ SUCCESS - Generated {len(df)} rows with {len(df.columns)} columns")
            
            # Show data types
            print(f"\nColumn Types:")
            for col in df.columns:
                print(f"  - {col}: {df[col].dtype}")
            
            # Show sample statistics for numeric columns
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
            if len(numeric_cols) > 0:
                print(f"\nNumeric Column Statistics:")
                for col in numeric_cols:
                    print(f"  - {col}: min={df[col].min():.2f}, max={df[col].max():.2f}, mean={df[col].mean():.2f}")
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n\n{'='*80}")
    print("ALL TESTS COMPLETED")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    test_prompt_generation()
