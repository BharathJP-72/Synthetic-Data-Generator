import pandas as pd
from ydata_synthetic.synthesizers import ModelParameters, TrainParameters
from ydata_synthetic.synthesizers.regular import RegularSynthesizer

# --- Step 1: Load CSV ---
try:
    file_path = input("Enter the path to your CSV file: ").strip()
    df = pd.read_csv(file_path)
    print(f"\n✅ Successfully loaded '{file_path}'. Shape: {df.shape}")
except FileNotFoundError:
    print(f"❌ Error: The file '{file_path}' was not found.")
    exit()

# --- Step 2: Detect Column Types ---
num_cols = df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
cat_cols = df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()

print(f"\n🔎 Detected Numeric columns: {num_cols}")
print(f"🔎 Detected Categorical columns: {cat_cols}")

if not num_cols and not cat_cols:
    print("❌ Error: No usable numeric or categorical columns were found.")
    exit()
    
# --- Step 3: Configure and Train CTGAN model ---
print("\n🤖 Initializing CTGAN for Tabular Data.")
n_samples = int(input("Enter the number of synthetic rows to generate: "))

model_params = ModelParameters(batch_size=500,
                               lr=2e-4,
                               betas=(0.5, 0.9))
train_params = TrainParameters(epochs=300)

synth = RegularSynthesizer(modelname='ctgan', model_parameters=model_params)

print("\n⏳ Training CTGAN model...")
synth.fit(data=df, train_arguments=train_params, num_cols=num_cols, cat_cols=cat_cols)

print("Sampling new data...")
synthetic_data = synth.sample(n_samples=n_samples)


# --- Step 4: Save the Generated Data ---
output_filename = "synthetic_data_ctgan.csv"
synthetic_data.to_csv(output_filename, index=False)
print(f"\n🎉 Synthetic data successfully generated and saved as '{output_filename}'")