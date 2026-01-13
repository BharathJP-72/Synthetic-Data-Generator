from src.core.engine import SyntheticDataEngine
from src.generators.prompt_generator import PromptGenerator

# Start engine
engine = SyntheticDataEngine()
engine.register_generator('prompt', PromptGenerator())

# Generate data
data = engine.generate_from_prompt(
    prompt="Customer names, emails, ages 18-65",
    num_rows=10
)

# Print it
print(data)