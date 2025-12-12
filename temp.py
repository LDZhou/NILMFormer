"""Verify PecanStreet_DataBuilder threshold keys are correct"""
import json
import sys
sys.path.insert(0, '.')

from src.helpers.preprocessing import PecanStreet_DataBuilder

# Test initialization
builder = PecanStreet_DataBuilder(
    data_path="data/pecanstreet/",
    mask_app="hvac",
    sampling_rate="1min",
    window_size=128,
)

print("=" * 50)
print("Threshold key validation:")
print("=" * 50)

# Check appliance_param has correct keys
for app, th in builder.appliance_param.items():
    has_min = 'min_threshold' in th
    has_max = 'max_threshold' in th
    print(f"\n{app}:")
    print(f"  min_threshold: {th.get('min_threshold', 'MISSING')} {'✓' if has_min else '✗'}")
    print(f"  max_threshold: {th.get('max_threshold', 'MISSING')} {'✓' if has_max else '✗'}")

# Test loading data
print("\n" + "=" * 50)
print("Testing data loading...")
print("=" * 50)

with open('data/pecanstreet/pecan_processed/groups_meta.json') as f:
    meta = json.load(f)

houses = meta['hvac']['houses'][:2]  # Test with 2 houses
print(f"Loading houses: {houses}")

try:
    data, st_date = builder.get_nilm_dataset(house_indicies=houses)
    print(f"\n✓ Data loaded successfully!")
    print(f"  Shape: {data.shape}")
    print(f"  Grid power mean: {data[:, 0, 0, :].mean():.4f}")
    print(f"  Appliance power mean: {data[:, 1, 0, :].mean():.4f}")
    print(f"  Appliance ON rate: {(data[:, 1, 1, :] > 0).mean()*100:.1f}%")
except KeyError as e:
    print(f"\n✗ KeyError: {e}")
    print("  Threshold keys still incorrect!")
except Exception as e:
    print(f"\n✗ Error: {e}")