import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Ensure plots directory exists
os.makedirs('plots', exist_ok=True)

# Set style for presentation-quality plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def load_data():
    """Load simulation results and tick stats from CSV files."""
    results = pd.read_csv('data/sim_results.csv')
    tick_stats = pd.read_csv('data/sim_tick_stats.csv')
    return results, tick_stats

def plot_tick_distribution(results):
    """Plot tick count distribution with histogram and box plot."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Histogram with KDE
    ax1.hist(results['ticks_to_complete'], bins=30, edgecolor='black', alpha=0.7, color='steelblue')
    ax1.axvline(results['ticks_to_complete'].mean(), color='red', linestyle='--',
                linewidth=2, label=f'Mean: {results["ticks_to_complete"].mean():.1f}')
    ax1.axvline(results['ticks_to_complete'].median(), color='orange', linestyle='--',
                linewidth=2, label=f'Median: {results["ticks_to_complete"].median():.1f}')
    ax1.set_xlabel('Ticks to Complete', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Frequency', fontsize=12, fontweight='bold')
    ax1.set_title('Distribution of Simulation Completion Times', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Box plot
    bp = ax2.boxplot(results['ticks_to_complete'], vert=True, patch_artist=True)
    bp['boxes'][0].set_facecolor('lightblue')
    bp['medians'][0].set_color('red')
    bp['medians'][0].set_linewidth(2)
    ax2.set_ylabel('Ticks to Complete', fontsize=12, fontweight='bold')
    ax2.set_title('Completion Time Summary', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')

    # Add statistics text
    stats_text = f"Min: {results['ticks_to_complete'].min()}\n"
    stats_text += f"Q1: {results['ticks_to_complete'].quantile(0.25):.1f}\n"
    stats_text += f"Median: {results['ticks_to_complete'].median():.1f}\n"
    stats_text += f"Q3: {results['ticks_to_complete'].quantile(0.75):.1f}\n"
    stats_text += f"Max: {results['ticks_to_complete'].max()}"
    ax2.text(1.15, 0.5, stats_text, transform=ax2.transAxes,
             fontsize=10, verticalalignment='center',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.savefig('plots/ticks_hist.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: plots/ticks_hist.png")
    plt.close()

def plot_reservation_pressure(tick_stats):
    """Plot reservation pressure and active cars over time."""
    first_run = tick_stats[tick_stats['run_id'] == tick_stats['run_id'].min()]

    fig, ax1 = plt.subplots(figsize=(12, 6))

    color1 = 'tab:blue'
    ax1.set_xlabel('Tick', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Reserved Cells (Space-Time)', fontsize=12, fontweight='bold', color=color1)
    ax1.plot(first_run['tick'], first_run['reserved_size'],
             color=color1, linewidth=2.5, label='Reserved Cells')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx()
    color2 = 'tab:red'
    ax2.set_ylabel('Active Cars', fontsize=12, fontweight='bold', color=color2)
    ax2.plot(first_run['tick'], first_run['active_cars'],
             color=color2, linewidth=2.5, linestyle='--', label='Active Cars')
    ax2.tick_params(axis='y', labelcolor=color2)

    plt.title('Reservation Pressure vs Active Cars (Single Run)', fontsize=14, fontweight='bold')

    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

    plt.tight_layout()
    plt.savefig('plots/reservation_pressure.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: plots/reservation_pressure.png")
    plt.close()

def main():
    """Generate the two required plots from simulation data."""
    print("\n" + "="*60)
    print("Generating visualization plots...")
    print("="*60 + "\n")

    results, tick_stats = load_data()

    print(f"Loaded {len(results)} simulation runs")
    print(f"Loaded {len(tick_stats)} tick-level records\n")

    plot_tick_distribution(results)
    plot_reservation_pressure(tick_stats)

    print("\n" + "="*60)
    print("Plots generated successfully!")
    print("Generated files:")
    print("  - plots/ticks_hist.png")
    print("  - plots/reservation_pressure.png")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
