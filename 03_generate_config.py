import json
import yaml
import numpy as np

with open('data/pecanstreet/pecan_processed/groups_meta.json') as f:
    meta = json.load(f)

config = {'PECANSTREET': {}}

for group, info in meta.items():
    houses = np.array(info['houses'])
    n = len(houses)
    
    if n == 0:
        continue
    
    # Split: 60% train, 20% valid, 20% test
    np.random.seed(42)
    np.random.shuffle(houses)
    
    n_train = max(1, int(n * 0.6))
    n_valid = max(1, int(n * 0.2))
    
    train = houses[:n_train].tolist()
    valid = houses[n_train:n_train+n_valid].tolist()
    test = houses[n_train+n_valid:].tolist()
    
    # Fallback if split too small
    if len(valid) == 0:
        valid = [train[-1]]
    if len(test) == 0:
        test = [train[0]] if len(train) > 1 else valid
    
    config['PECANSTREET'][group] = {
        'app': group,
        'house_with_app_i': houses.tolist()
    }

with open('configs/datasets.yaml', 'r') as f:
    existing = yaml.safe_load(f) or {}

existing.update(config)

with open('configs/datasets.yaml', 'w') as f:
    yaml.dump(existing, f, default_flow_style=False)

print("Generated config:")
for group, cfg in config['PECANSTREET'].items():
    print(f"{group}: {len(cfg['house_with_app_i'])} houses")