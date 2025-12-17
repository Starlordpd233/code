import random
import csv
import os
from CarSimTools import Grid

# Ensure directories exist
os.makedirs('data', exist_ok=True)
os.makedirs('plots', exist_ok=True)

def run_single_simulation(seed, max_ticks=10000):
    """Run a single simulation with given seed and return results."""
    random.seed(seed)
    grid = Grid()

    tick = 0
    while not grid.complete() and tick < max_ticks:
        grid.updateAll()
        grid.step()
        tick += 1

    return {
        'run_id': seed,
        'seed': seed,
        'ticks_to_complete': tick,
        'completed': grid.complete(),
        'tick_stats': grid.tick_stats
    }

def run_many_simulations(num_runs=500, base_seed=42, max_ticks=10000):
    """Run multiple simulations and save results to CSV files."""
    print(f"Running {num_runs} simulations...")

    run_results = []
    all_tick_stats = []

    for i in range(num_runs):
        seed = base_seed + i

        if (i + 1) % 50 == 0:
            print(f"  Completed {i + 1}/{num_runs} runs")

        result = run_single_simulation(seed, max_ticks)

        run_results.append({
            'run_id': result['run_id'],
            'seed': result['seed'],
            'ticks_to_complete': result['ticks_to_complete'],
            'completed': result['completed']
        })

        for stat in result['tick_stats']:
            all_tick_stats.append({
                'run_id': result['run_id'],
                **stat
            })

    # Write run summaries
    print("\nWriting results to CSV files...")
    with open('1.4_car_project/data/sim_results.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['run_id', 'seed', 'ticks_to_complete', 'completed'])
        writer.writeheader()
        writer.writerows(run_results)

    # Write tick-level statistics
    with open('1.4_car_project/data/sim_tick_stats.csv', 'w', newline='') as f:
        fieldnames = ['run_id', 'tick', 'active_cars', 'reserved_size']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_tick_stats)

    completed_runs = sum(1 for r in run_results if r['completed'])
    avg_ticks = sum(r['ticks_to_complete'] for r in run_results) / len(run_results)

    print(f"\n{'='*60}")
    print(f"Batch run complete!")
    print(f"  Total runs: {num_runs}")
    print(f"  Completed: {completed_runs} ({100*completed_runs/num_runs:.1f}%)")
    print(f"  Average ticks: {avg_ticks:.1f}")
    print(f"  Results saved to: data/sim_results.csv")
    print(f"  Tick stats saved to: data/sim_tick_stats.csv")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    run_many_simulations(num_runs=500, base_seed=42, max_ticks=10000)
