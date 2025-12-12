#!/usr/bin/env python3
"""
01_prepare_pecan.py - Prepare PecanStreet data for NILMFormer

This script:
1. Loads raw PecanStreet 1-minute data
2. Identifies houses with sufficient appliance data for each group
3. Generates groups_meta.json with proper threshold keys (min_threshold/max_threshold)
"""

import os
import json
import pandas as pd
import numpy as np
from pathlib import Path

# Import group definitions
from groups import GROUPS

# ============= Configuration =============
DATA_PATH = "data/pecanstreet/"
RAW_FILE = "1minute_data_austin.csv"
OUTPUT_DIR = "data/pecanstreet/pecan_processed/"
MIN_HOURS = 720  # Minimum 30 days of data per house
MIN_ON_RATE = 0.05  # Minimum 5% ON time for an appliance

# ============= Helper Functions =============
def find_houses_with_appliance(df, group_name, group_info, min_hours=MIN_HOURS, min_on_rate=MIN_ON_RATE):
    """Find houses that have sufficient data for a given appliance group"""
    cols = group_info['cols']
    th = group_info['threshold']
    
    # Normalize threshold keys
    min_th = th.get('min_threshold', th.get('min', 0.02))
    max_th = th.get('max_threshold', th.get('max', 10.0))
    
    valid_houses = []
    house_stats = {}
    
    for house_id in df['dataid'].unique():
        house = df[df['dataid'] == house_id]
        
        # Check if house has any of the group columns
        available_cols = [c for c in cols if c in house.columns]
        if not available_cols:
            continue
        
        # Sum power from all available columns in the group
        power = house[available_cols].sum(axis=1, min_count=1).fillna(0)
        
        # Calculate statistics
        total_points = len(power)
        if total_points < min_hours * 60:  # Less than minimum hours
            continue
        
        # Calculate ON rate
        on_mask = (power >= min_th) & (power <= max_th)
        on_rate = on_mask.sum() / total_points
        
        if on_rate >= min_on_rate:
            valid_houses.append(house_id)
            house_stats[house_id] = {
                'total_hours': total_points / 60,
                'on_rate': on_rate,
                'mean_power': power[on_mask].mean() if on_mask.any() else 0,
                'available_cols': available_cols
            }
    
    return valid_houses, house_stats


def main():
    print("=" * 60)
    print("PecanStreet Data Preparation for NILMFormer")
    print("=" * 60)
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Load data
    raw_path = os.path.join(DATA_PATH, RAW_FILE)
    print(f"\nLoading data from {raw_path}...")
    df = pd.read_csv(raw_path)
    df['localminute'] = pd.to_datetime(df['localminute'], utc=True)
    
    print(f"  Total rows: {len(df):,}")
    print(f"  Total houses: {df['dataid'].nunique()}")
    print(f"  Date range: {df['localminute'].min()} to {df['localminute'].max()}")
    
    # Process each group
    groups_meta = {}
    
    print("\n" + "-" * 60)
    print("Processing appliance groups...")
    print("-" * 60)
    
    for group_name, group_info in GROUPS.items():
        print(f"\n[{group_name}] {group_info['desc']}")
        print(f"  Columns: {group_info['cols']}")
        
        # Get threshold with normalized keys
        th = group_info['threshold']
        min_th = th.get('min_threshold', th.get('min', 0.02))
        max_th = th.get('max_threshold', th.get('max', 10.0))
        print(f"  Threshold: {min_th} - {max_th} kW")
        
        # Find valid houses
        valid_houses, house_stats = find_houses_with_appliance(
            df, group_name, group_info, MIN_HOURS, MIN_ON_RATE
        )
        
        print(f"  Valid houses: {len(valid_houses)}")
        
        if valid_houses:
            # Store metadata with NORMALIZED threshold keys
            groups_meta[group_name] = {
                'cols': group_info['cols'],
                'threshold': {
                    'min_threshold': float(min_th),  # Always use min_threshold
                    'max_threshold': float(max_th)   # Always use max_threshold
                },
                'desc': group_info['desc'],
                'houses': [int(h) for h in valid_houses],  # Convert to native int
                'stats': {
                    'n_houses': len(valid_houses),
                    'avg_on_rate': float(np.mean([s['on_rate'] for s in house_stats.values()])),
                    'avg_power': float(np.mean([s['mean_power'] for s in house_stats.values()]))
                }
            }
            
            # Print top houses
            if house_stats:
                sorted_houses = sorted(house_stats.items(), key=lambda x: x[1]['on_rate'], reverse=True)
                print(f"  Top 3 houses by ON rate:")
                for h, s in sorted_houses[:3]:
                    print(f"    House {h}: {s['on_rate']*100:.1f}% ON, {s['total_hours']:.0f} hours")
    
    # Save metadata
    meta_path = os.path.join(OUTPUT_DIR, "groups_meta.json")
    with open(meta_path, 'w') as f:
        json.dump(groups_meta, f, indent=2)
    print(f"\n{'=' * 60}")
    print(f"Saved groups_meta.json to {meta_path}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    for group_name, meta in groups_meta.items():
        print(f"  {group_name}: {meta['stats']['n_houses']} houses, "
              f"avg ON rate {meta['stats']['avg_on_rate']*100:.1f}%")
    
    # Verify threshold keys
    print("\n" + "-" * 60)
    print("Threshold Key Verification:")
    print("-" * 60)
    for group_name, meta in groups_meta.items():
        th = meta['threshold']
        has_correct_keys = 'min_threshold' in th and 'max_threshold' in th
        status = "✓" if has_correct_keys else "✗"
        print(f"  {status} {group_name}: {th}")
    
    print("\nDone!")


if __name__ == "__main__":
    main()