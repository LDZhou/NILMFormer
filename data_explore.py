import pandas as pd
import numpy as np

# Load data
df = pd.read_csv('data/pecanstreet/1minute_data_austin.csv')

# Basic info
print("="*50)
print("Data Shape:", df.shape)
print("\n" + "="*50)
print("Column Names:")
print(df.columns.tolist())

print("\n" + "="*50)
print("First 5 rows:")
print(df.head())

print("\n" + "="*50)
print("Data Types:")
print(df.dtypes)

print("\n" + "="*50)
print("Missing Values:")
print(df.isnull().sum())

print("\n" + "="*50)
print("Basic Statistics:")
print(df.describe())

# Check if there's a timestamp column
timestamp_cols = [col for col in df.columns if 'time' in col.lower() or 'date' in col.lower()]
print("\n" + "="*50)
print("Timestamp columns:", timestamp_cols)

if timestamp_cols:
    print("\nTime range:")
    for col in timestamp_cols:
        print(f"{col}: {df[col].min()} to {df[col].max()}")