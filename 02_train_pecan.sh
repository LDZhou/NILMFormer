#!/bin/bash
#SBATCH -A eecs
#SBATCH -p ampere
#SBATCH --gres=gpu:1
#SBATCH --time=48:00:00
#SBATCH --mem=32G
#SBATCH --output=logs/train_%j.log

mkdir -p logs
source ~/.bashrc
conda activate ai_env

for app in hvac waterheater ev laundry dishwasher refrigeration kitchen; do
    for s in 0 1 2; do
        echo "Training: ${app} seed=${s}"
        python -m scripts.run_one_expe \
            --dataset PECANSTREET \
            --sampling_rate 1min \
            --appliance ${app} \
            --window_size 128 \
            --name_model NILMFormer \
            --seed ${s}
    done
done
EOF