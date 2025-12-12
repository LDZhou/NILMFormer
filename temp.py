import pandas as pd
import numpy as np
from groups import GROUPS
import json

df = pd.read_csv('data/pecanstreet/1minute_data_austin.csv')
with open('data/pecan_processed/groups_meta.json') as f:
    meta = json.load(f)

print("Group Threshold Analysis\n")

for name, info in GROUPS.items():
    if name not in meta or meta[name]['count'] == 0:
        continue
    
    print(f"{'='*60}")
    print(f"{name.upper()}: {info['desc']}")
    print(f"  Houses: {meta[name]['count']}")
    print(f"  Current threshold: min={info['threshold']['min']:.3f}, max={info['threshold']['max']:.3f}")
    
    cols = meta[name]['cols']
    houses = meta[name]['houses']
    
    all_power, on_rates = [], []
    for house_id in houses:
        power = df[df['dataid'] == house_id][cols].sum(axis=1, min_count=1)
        power = power[power.notna() & (power > 0)]
        if len(power) > 0:
            all_power.extend(power.values)
            th = info['threshold']
            on_rate = ((power >= th['min']) & (power <= th['max'])).mean()
            on_rates.append(on_rate)
    
    if all_power:
        all_power = np.array(all_power)
        print(f"\n  Power distribution (kW):")
        print(f"    Mean={all_power.mean():.3f}, Median={np.median(all_power):.3f}")
        print(f"    P5={np.percentile(all_power, 5):.3f}, P95={np.percentile(all_power, 95):.3f}")
        print(f"    P99={np.percentile(all_power, 99):.3f}, Max={all_power.max():.3f}")
        
        avg_on = np.mean(on_rates)
        print(f"\n  ON rate: {avg_on*100:.1f}%")
        
        p5, p95 = np.percentile(all_power, 5), np.percentile(all_power, 95)
        print(f"  Suggested: min={p5:.3f}, max={p95:.3f}")
        
        if avg_on < 0.05:
            print(f"  ⚠️  ON rate too low, threshold too strict")
        elif avg_on > 0.8:
            print(f"  ⚠️  ON rate too high, threshold too loose")
        else:
            print(f"  ✓ Threshold reasonable")

print(f"\n{'='*60}")