# NVIDIA Nemotron Integration Setup

## Overview

The synthetic data generator now uses **NVIDIA Nemotron 70B** for intelligent prompt understanding! This provides much better field extraction and type detection.

## Setup Instructions

### Step 1: Get NVIDIA API Key (FREE)

1. Visit [build.nvidia.com](https://build.nvidia.com)
2. Search for "Nemotron" in the search bar
3. Click on "Llama 3.1 Nemotron 70B Instruct"
4. Click "Get API Key" button on the right side
5. Sign in with your NVIDIA account (create one if needed)
6. Copy your API key

### Step 2: Configure API Key

Create a `.env` file in the project root:

```bash
# In: C:\Users\Dayanand S G\OneDrive\Desktop\synthetic-data-generator\.env
NVIDIA_API_KEY=your_api_key_here
```

**OR** set as environment variable:

```powershell
# Windows PowerShell
$env:NVIDIA_API_KEY="your_api_key_here"

# Windows CMD
set NVIDIA_API_KEY=your_api_key_here
```

### Step 3: Test the Integration

Run the test script:

```bash
python test_nemotron_integration.py
```

## How It Works

### With Nemotron (Recommended)

When API key is configured:
1. Prompt is sent to Nemotron 70B LLM
2. LLM intelligently extracts field names and types
3. Returns structured schema with correct mappings

**Example:**
- Input: "online orders including customer IDs, product names, quantities, prices, order timestamps"
- Nemotron correctly identifies:
  - `customer_ids` → person.identifier
  - `product_names` → food.dish (realistic products!)
  - `quantities` → integer (1-100)
  - `prices` → float (10-1000)
  - `order_timestamps` → datetime (2020-2024)

### Without Nemotron (Fallback)

If no API key is configured:
- Falls back to improved regex-based parsing
- Still works, but less accurate for complex prompts
- Free, no API calls

## Benefits of Nemotron

✅ **Accurate Field Detection**: Correctly identifies "product names" as products, not person names
✅ **Context Awareness**: Understands "quantities" should be numbers, not names
✅ **Natural Language**: Write prompts in plain English
✅ **Free Tier**: NVIDIA provides free API access
✅ **Automatic Fallback**: Works offline with regex if API unavailable

## Usage

Just use the prompt-based generator as before:

```python
from src.core.engine import SyntheticDataEngine
from src.generators.mimesis_generator import MimesisGenerator

engine = SyntheticDataEngine()
engine.register_generator("mimesis", MimesisGenerator())

# Nemotron will automatically parse this intelligently!
df = engine.generate_from_prompt(
    "online orders including customer IDs, product names, quantities, prices, order timestamps",
    num_rows=100
)
```

## Troubleshooting

### "NVIDIA_API_KEY not found"
- Make sure `.env` file is in project root
- Or set environment variable before running

### "Nemotron parsing failed"
- Check your API key is valid
- Verify internet connection
- System will automatically fall back to regex parsing

### "Rate limit exceeded"
- NVIDIA free tier has rate limits
- Wait a few minutes and try again
- Or use smaller prompts

## API Costs

- **Free Tier**: Generous free quota for testing
- **Paid Tier**: Very affordable for production use
- **Fallback**: Always free (regex-based)
