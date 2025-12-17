# CarSim Visualization Suite (Minimal Version)

Lightweight visualization toolkit for the greedy reservation algorithm.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Complete Workflow

```bash
# Step 1: Run batch simulations (creates data/)
python run_many.py

# Step 2: Generate the two plots (creates plots/)
python plot_results.py
```

---

## Output Files

### Data Files (in `data/`)
- **sim_results.csv**: Summary of each simulation run (run_id, seed, ticks_to_complete, completed)
- **sim_tick_stats.csv**: Per-tick statistics (tick, active_cars, reserved_size)

### Plot Files (in `plots/`)
- **ticks_hist.png**: Tick count distribution (histogram + box plot)
- **reservation_pressure.png**: Reserved cells vs active cars over time

---

## What Each Plot Shows

### 1. Tick Count Distribution (ticks_hist.png)
- **Left panel**: Histogram showing how many runs completed at each tick count
- **Right panel**: Box plot with quartile statistics
- **Purpose**: Shows overall performance and variability across 500 runs
- **Key metrics**: Mean, median, min, max, quartiles

### 2. Reservation Pressure (reservation_pressure.png)
- **Blue line**: Number of space-time cells reserved at each tick
- **Red dashed line**: Number of active cars at each tick
- **Purpose**: Visualizes how the space-time reservation system creates pressure
- **Key insight**: Reserved cells can exceed 100 because each car reserves its entire future path

---

## Understanding the Metrics

### Active Cars
Number of cars currently on the grid (not waiting in queue)

### Reserved Cells (Space-Time)
Total number of (row, col, tick) tuples reserved
- Can exceed 100 because it tracks position AND time
- Example: (5, 5, tick=10) and (5, 5, tick=15) are different reservations

---

## Minimal Instrumentation in CarSimTools.py

Only one field added:
```python
self.tick_stats = []  # List storing {tick, active_cars, reserved_size} per tick
```

This is **read-only instrumentation**—it doesn't affect your algorithm's behavior, only records data for visualization.

---

## Customization

### Change number of runs
In `run_many.py`:
```python
run_many_simulations(num_runs=1000, base_seed=42, max_ticks=10000)
```

### Change which run to visualize
In `plot_results.py`, the reservation pressure plot uses the first run (run_id = min). To change:
```python
# Use a specific seed
specific_run = tick_stats[tick_stats['run_id'] == 42]
```

---

## Troubleshooting

### "No such file: data/sim_results.csv"
Run `python run_many.py` first to generate data.

### Plots look different
Make sure you're running from the `1.4_car_project` directory so relative paths work correctly.

---

## File Summary

| File | Purpose | What It Does |
|------|---------|--------------|
| `CarSimTools.py` | Core simulation | Tracks tick_stats for visualization |
| `run_many.py` | Batch runner | Runs 500 simulations, saves CSV data |
| `plot_results.py` | Static plots | Generates 2 PNG plots |
| `requirements.txt` | Dependencies | pandas, matplotlib, seaborn, numpy |
| `VISUALS.md` | Documentation | This file |

---

## Note About make_gif.py

The `make_gif.py` script is **not functional** with the minimal instrumentation. It requires additional tracking that was removed to keep CarSimTools.py clean for submission. If you need the GIF, restore the full instrumentation from the original version.
