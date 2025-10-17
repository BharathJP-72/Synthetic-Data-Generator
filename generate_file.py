from file_based.ydata_model import train_model, generate_synthetic
import pandas as pd

# Load real data
df = pd.read_csv("data/real_data.csv")

# Train model (if not already trained)
train_model(df, model_path="models/ctgan_model.pkl")

# Generate synthetic data
synthetic_df = generate_synthetic("models/ctgan_model.pkl", 1000)
synthetic_df.to_csv("data/synthetic_data.csv", index=False)
print("Synthetic data saved!")
