import pandas as pd
import numpy as np
import json
from pathlib import Path
from groups import GROUPS

df = pd.read_csv('data/pecanstreet/1minute_data_austin.csv')
df['localminute'] = pd.to_datetime(df['localminute'], utc=True)
Path('data/pecanstreet/pecan_processed').mkdir(parents=True, exist_ok=True)

stats = {}
for name, info in GROUPS.items():
    print(f"\n{name}: {info['desc']}")
    cols = [c for c in info['cols'] if c in df.columns]
    if not cols:
        print(f"  No data")
        continue
    
    houses = {}
    for dataid in df['dataid'].unique():
        power = df[df['dataid'] == dataid][cols].sum(axis=1, min_count=1)
        coverage = power.notna().mean()
        activity = (power > 0.01).mean()
        if coverage > 0.8 and activity > 0.01:
            houses[dataid] = {'coverage': coverage, 'activity': activity}
    
    stats[name] = {
        'cols': cols,
        'threshold': info['threshold'],
        'houses': [int(h) for h in sorted(houses.keys())],
        'count': len(houses)
    }
    print(f"  Cols: {len(cols)}/{len(info['cols'])}, Houses: {len(houses)}")

with open('data/pecanstreet/pecan_processed/groups_meta.json', 'w') as f:
    json.dump(stats, f, indent=2)

print(f"\nSummary:")
for name, s in stats.items():
    print(f"  {name:15s}: {s['count']:3d} houses")
print(f"\nSaved: data/pecanstreet/pecan_processed/groups_meta.json")