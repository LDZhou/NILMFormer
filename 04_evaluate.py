#!/usr/bin/env python3
"""
04_read_results.py - Read metrics from trained checkpoints

Usage:
    python 04_read_results.py --app hvac
    python 04_read_results.py --app ev
    python 04_read_results.py  # Read all
"""

import torch
import numpy as np
import argparse
from pathlib import Path

RESULT_PATH = "result/"

def read_checkpoint_metrics(ckpt_path):
    """Read metrics from checkpoint"""
    ckpt = torch.load(ckpt_path, map_location='cpu', weights_only=False)
    
    metrics = {}
    for k, v in ckpt.items():
        if 'test_metrics' in k or 'valid_metrics' in k:
            if isinstance(v, (int, float, np.floating)):
                metrics[k] = float(v)
            elif isinstance(v, np.ndarray):
                metrics[k] = {'shape': v.shape, 'mean': float(v.mean()), 'std': float(v.std())}
            elif isinstance(v, torch.Tensor):
                metrics[k] = {'shape': tuple(v.shape), 'mean': float(v.mean()), 'std': float(v.std())}
    
    # Also get training info
    metrics['training_time'] = ckpt.get('training_time', 'N/A')
    metrics['epoch_best_loss'] = ckpt.get('epoch_best_loss', 'N/A')
    metrics['value_best_loss'] = ckpt.get('value_best_loss', 'N/A')
    
    return metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--app', type=str, default=None, help='Appliance (hvac, ev, etc.)')
    args = parser.parse_args()
    
    result_dir = Path(RESULT_PATH)
    
    # Find all checkpoints
    if args.app:
        patterns = [f"PECANSTREET_{args.app}_*"]
    else:
        patterns = ["PECANSTREET_*"]
    
    for pattern in patterns:
        for app_dir in sorted(result_dir.glob(pattern)):
            print(f"\n{'='*70}")
            print(f"  {app_dir.name}")
            print(f"{'='*70}")
            
            for ckpt_file in sorted(app_dir.glob("**/*.pt")):
                print(f"\n--- {ckpt_file.name} ---")
                
                try:
                    metrics = read_checkpoint_metrics(ckpt_file)
                    
                    # Print key metrics
                    print(f"  Training time: {metrics.get('training_time', 'N/A')}")
                    print(f"  Best epoch: {metrics.get('epoch_best_loss', 'N/A')}")
                    print(f"  Best loss: {metrics.get('value_best_loss', 'N/A')}")
                    
                    # Test metrics
                    print(f"\n  Test Metrics:")
                    for k, v in sorted(metrics.items()):
                        if k.startswith('test_metrics'):
                            name = k.replace('test_metrics_', '')
                            if isinstance(v, dict):
                                print(f"    {name}: mean={v['mean']:.4f}, std={v['std']:.4f}, shape={v['shape']}")
                            else:
                                print(f"    {name}: {v:.4f}" if isinstance(v, float) else f"    {name}: {v}")
                    
                    # Valid metrics
                    print(f"\n  Validation Metrics:")
                    for k, v in sorted(metrics.items()):
                        if k.startswith('valid_metrics'):
                            name = k.replace('valid_metrics_', '')
                            if isinstance(v, dict):
                                print(f"    {name}: mean={v['mean']:.4f}, std={v['std']:.4f}, shape={v['shape']}")
                            else:
                                print(f"    {name}: {v:.4f}" if isinstance(v, float) else f"    {name}: {v}")
                                
                except Exception as e:
                    print(f"  Error loading: {e}")
    
    # Summary table
    print(f"\n{'='*70}")
    print("SUMMARY TABLE")
    print(f"{'='*70}")
    print(f"{'App':<15} {'Seed':<6} {'Test D':<12} {'Test W':<12} {'Test ME':<12}")
    print("-" * 70)
    
    for app_dir in sorted(result_dir.glob("PECANSTREET_*")):
        app_name = app_dir.name.replace("PECANSTREET_", "").replace("_1min", "")
        
        for ckpt_file in sorted(app_dir.glob("**/*.pt")):
            seed = ckpt_file.stem.split("_")[-1]
            
            try:
                ckpt = torch.load(ckpt_file, map_location='cpu', weights_only=False)
                
                test_D = ckpt.get('test_metrics_D', 'N/A')
                test_W = ckpt.get('test_metrics_W', 'N/A')
                test_ME = ckpt.get('test_metrics_ME', 'N/A')
                
                # Handle different types
                def fmt(v):
                    if isinstance(v, (np.ndarray, torch.Tensor)):
                        return f"{float(v.mean()):.4f}"
                    elif isinstance(v, (int, float, np.floating)):
                        return f"{float(v):.4f}"
                    return str(v)
                
                print(f"{app_name:<15} {seed:<6} {fmt(test_D):<12} {fmt(test_W):<12} {fmt(test_ME):<12}")
                
            except Exception as e:
                print(f"{app_name:<15} {seed:<6} Error: {e}")


if __name__ == "__main__":
    main()