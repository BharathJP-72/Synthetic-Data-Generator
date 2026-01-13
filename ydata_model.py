import pandas as pd
from ydata_synthetic.synthesizers import ModelParameters, TrainParameters
from ydata_synthetic.synthesizers.regular import RegularSynthesizer

# Step 1: Load CSV dynamically
file_path = input("Enter the path to your CSV file: ").strip()
df = pd.read_csv(file_path)

# Step 2: Detect numeric and categorical columns
num_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

print(f"Numeric columns: {num_cols}")
print(f"Categorical columns: {cat_cols}")

# Step 3: Set parameters
model_params = ModelParameters(batch_size=500, lr=2e-4, betas=(0.5, 0.9))
train_params = TrainParameters(epochs=300)

# Step 4: Initialize RegularSynthesizer for CTGAN
synth = RegularSynthesizer(modelname="ctgan", model_parameters=model_params)

# Step 5: Train
synth.fit(df, train_arguments=train_params, num_cols=num_cols, cat_cols=cat_cols)

# Step 6: Generate synthetic data
n_samples = int(input("Enter number of synthetic rows to generate: "))
synthetic_data = synth.sample(n_samples)

# Step 7: Save to CSV
synthetic_data.to_csv("synthetic_data.csv", index=False)
print("Synthetic data saved as 'synthetic_data11.csv'")
