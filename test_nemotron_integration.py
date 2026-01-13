"""
Test NVIDIA Nemotron integration for prompt-based generation.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.engine import SyntheticDataEngine
from src.generators.mimesis_generator import MimesisGenerator

def test_nemotron_integration():
    """Test Nemotron-powered prompt parsing."""
    
    print("=" * 80)
    print("TESTING NVIDIA NEMOTRON INTEGRATION")
    print("=" * 80)
    print()
    
    # Initialize engine
    engine = SyntheticDataEngine()
    engine.register_generator("mimesis", MimesisGenerator())
    
    # Test the original problematic prompt
    test_prompt = "online orders including customer IDs, product names, quantities, prices, order timestamps"
    
    print(f"Test Prompt: {test_prompt}")
    print()
    print("Generating data...")
    print()
    
    try:
        # Generate data
        df = engine.generate_from_prompt(test_prompt, 20)
        
        print("✅ SUCCESS! Generated data:")
        print("=" * 80)
        print(df.to_string())
        print()
        print("=" * 80)
        print()
        
        # Show column info
        print("Column Information:")
        for col in df.columns:
            print(f"  - {col}: {df[col].dtype}")
            if df[col].dtype in ['int64', 'float64']:
                print(f"    Range: {df[col].min()} to {df[col].max()}")
            else:
                print(f"    Sample: {df[col].iloc[0]}")
        print()
        
        # Verify correctness
        print("Verification:")
        print("=" * 80)
        
        # Check if product names are realistic (not person names)
        if 'product_names' in df.columns:
            sample_product = str(df['product_names'].iloc[0])
            print(f"✓ Product Name Sample: '{sample_product}'")
            print(f"  (Should be food/product, not person name)")
        
        # Check if quantities are numbers
        if 'quantities' in df.columns:
            if df['quantities'].dtype in ['int64', 'float64']:
                print(f"✓ Quantities are numeric: {df['quantities'].dtype}")
                print(f"  Range: {df['quantities'].min()} to {df['quantities'].max()}")
            else:
                print(f"❌ Quantities are NOT numeric: {df['quantities'].dtype}")
        
        # Check if prices are numbers
        if 'prices' in df.columns:
            if df['prices'].dtype in ['int64', 'float64']:
                print(f"✓ Prices are numeric: {df['prices'].dtype}")
                print(f"  Range: {df['prices'].min():.2f} to {df['prices'].max():.2f}")
            else:
                print(f"❌ Prices are NOT numeric: {df['prices'].dtype}")
        
        print()
        print("=" * 80)
        print("TEST COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_nemotron_integration()
