# ML Model Training Optimization

The original Karpathy autoresearch domain. Optimize training code to minimize validation loss within a fixed time budget.

## Typical Metrics

| Metric Name    | Unit          | Direction | Extraction Example              |
| -------------- | ------------- | --------- | ------------------------------- |
| `val_bpb`      | bits per byte | ↓ lower   | `grep "^val_bpb:" run.log`      |
| `val_loss`     | loss          | ↓ lower   | `grep "^val_loss:" run.log`     |
| `train_time_s` | seconds       | ↓ lower   | training script output          |
| `peak_vram_mb` | megabytes     | ↓ lower   | `grep "^peak_vram_mb:" run.log` |

## The Karpathy Setup

The canonical autoresearch setup:

1. **Mutable file:** `train.py` — architecture, optimizer, hyperparameters, everything
2. **Immutable harness:** `prepare.py` — data loading, evaluation function, time budget
3. **Fixed time budget:** Every experiment runs for exactly 5 minutes (300s)
4. **Single metric:** `val_bpb` (lower is better)

```bash
# Verify command
uv run train.py > run.log 2>&1 && grep "^val_bpb:" run.log | awk -F: '{print $2}'

# No guard needed — the training script validates itself
```

## What the Agent Can Modify

- Neural network architecture (layers, heads, dimensions, activation functions)
- Optimizer choice and configuration (learning rate, momentum, weight decay)
- All hyperparameters (batch size, sequence length, warmup steps)
- Training loop structure (gradient accumulation, mixed precision, compilation)
- Data loading strategy (shuffling, preprocessing, augmentation)

## What the Agent CANNOT Modify

- The evaluation function (`evaluate_bpb`)
- The data preparation script (`prepare.py`)
- The time budget (5 minutes per experiment)
- Package dependencies

## Fast-Fail Pattern

The training script should exit immediately on obvious failures:

```python
if math.isnan(train_loss) or train_loss > 100:
    print("FAIL")
    exit(1)
```

This prevents wasting 5 minutes on a clearly broken configuration — the experiment fails in seconds, gets logged as a crash, and the loop moves on.

## High-Impact Optimization Patterns

1. **Learning rate schedule** — warmup + cosine decay is usually optimal
2. **Architecture scaling** — width vs depth tradeoffs for fixed compute
3. **Optimizer choice** — Muon/AdamW hybrids, per-parameter LR
4. **Mixed precision** — bf16/fp16 for 2x throughput
5. **Torch compile** — `torch.compile(model)` for kernel fusion
6. **Gradient accumulation** — simulate larger batch sizes
7. **Data efficiency** — curriculum learning, data ordering

## Noise Handling

Training metrics are inherently noisy (random initialization, data shuffling). Mitigations:

- Set a fixed random seed for reproducibility
- Run each experiment with the same seed
- Only keep changes that improve by >0.5% to filter noise
- Track the metric at the same training step each time
