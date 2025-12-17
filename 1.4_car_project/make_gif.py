import random
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
# In some sandboxed environments the default Matplotlib config dir (often under ~/)
# may not be writable; default to a local, writable directory.
os.environ.setdefault("MPLCONFIGDIR", str(BASE_DIR / ".mplconfig"))

try:
    import matplotlib
    # Avoid Retina/HiDPI canvas scaling issues that can break manual reshapes.
    # Users can override by setting MPLBACKEND in their environment.
    if os.environ.get("MPLBACKEND") is None:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "Missing dependency. Install requirements with:\n"
        "  python3 -m pip install -r 1.4_car_project/requirements.txt"
    ) from exc

import numpy as np
import imageio.v2 as imageio
from CarSimTools import Grid, DIM

PLOTS_DIR = BASE_DIR / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def _figure_to_rgb_array(fig: "plt.Figure") -> np.ndarray:
    """
    Convert a Matplotlib figure into an RGB uint8 HxWx3 array.

    Uses the canvas' real pixel dimensions to avoid reshape errors on HiDPI displays.
    """
    fig.canvas.draw()
    try:
        rgba = np.asarray(fig.canvas.buffer_rgba(), dtype=np.uint8)
        return np.ascontiguousarray(rgba[:, :, :3])
    except Exception:
        width, height = fig.canvas.get_width_height()
        rgb = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        return rgb.reshape((height, width, 3))

def draw_frame(grid, ax, tick, newly_activated, lookahead_k=6):
    """Draw a single frame of the simulation."""
    ax.clear()
    ax.set_xlim(-0.5, DIM - 0.5)
    ax.set_ylim(-0.5, DIM - 0.5)
    ax.set_aspect('equal')
    ax.invert_yaxis()

    # Draw grid lines
    for i in range(DIM + 1):
        ax.axhline(i - 0.5, color='gray', linewidth=0.5, alpha=0.3)
        ax.axvline(i - 0.5, color='gray', linewidth=0.5, alpha=0.3)

    # Draw reserved cells (space-time reservations for next K ticks)
    reserved_cells = grid.last_reserved_cells_with_time
    reservation_counts = {}

    for (row, col, t) in reserved_cells:
        if tick <= t < tick + lookahead_k:
            key = (row, col)
            if key not in reservation_counts:
                reservation_counts[key] = []
            reservation_counts[key].append(t - tick)

    # Color reserved cells by proximity (darker = sooner)
    for (row, col), ticks_list in reservation_counts.items():
        min_tick_offset = min(ticks_list)
        intensity = 1.0 - (min_tick_offset / lookahead_k)
        color = plt.cm.Reds(0.3 + 0.5 * intensity)
        rect = patches.Rectangle((col - 0.4, row - 0.4), 0.8, 0.8,
                                 linewidth=0, facecolor=color, alpha=0.6)
        ax.add_patch(rect)

    # Draw path intent for active cars (faint lines showing planned route)
    for r in range(DIM):
        for c in range(DIM):
            car = grid.active[r][c]
            if car:
                current_row, current_col = r, c
                goal_row = car.get_goal().row
                goal_col = car.get_goal().col

                # Horizontal path
                if current_col < goal_col:
                    ax.plot([current_col, goal_col], [current_row, current_row],
                           'b--', linewidth=1.5, alpha=0.3)
                elif current_col > goal_col:
                    ax.plot([current_col, goal_col], [current_row, current_row],
                           'b--', linewidth=1.5, alpha=0.3)

                # Vertical path (from end of horizontal to goal)
                if current_row != goal_row:
                    ax.plot([goal_col, goal_col], [current_row, goal_row],
                           'b--', linewidth=1.5, alpha=0.3)

    # Draw active cars with directional arrows
    arrow_map = {0: '^', 1: 'v', 2: '<', 3: '>'}
    for r in range(DIM):
        for c in range(DIM):
            car = grid.active[r][c]
            if car:
                # Check if newly activated
                is_new = (r, c) in newly_activated
                color = 'lime' if is_new else 'blue'
                size = 400 if is_new else 250

                ax.scatter(c, r, s=size, c=color, marker=arrow_map[car.direction],
                          edgecolors='black', linewidths=1.5, zorder=10)

                # Add pulsing ring for newly activated
                if is_new:
                    circle = patches.Circle((c, r), radius=0.35, linewidth=2.5,
                                          edgecolor='yellow', facecolor='none',
                                          linestyle='--', zorder=9)
                    ax.add_patch(circle)

    # Draw goal markers for active cars
    for r in range(DIM):
        for c in range(DIM):
            car = grid.active[r][c]
            if car:
                goal = car.get_goal()
                ax.scatter(goal.col, goal.row, s=100, c='red', marker='*',
                          edgecolors='darkred', linewidths=1, zorder=8, alpha=0.6)

    # Title and labels
    active_count = sum(1 for row in grid.active for car in row if car)
    ax.set_title(f'Tick {tick} | Active Cars: {active_count} | '
                f'Reserved Cells: {len(reservation_counts)}',
                fontsize=14, fontweight='bold', pad=10)

    # Legend
    legend_elements = [
        plt.Line2D([0], [0], marker='^', color='w', markerfacecolor='blue',
                  markersize=10, label='Active Car'),
        plt.Line2D([0], [0], marker='^', color='w', markerfacecolor='lime',
                  markersize=12, label='Newly Activated'),
        plt.Line2D([0], [0], marker='*', color='w', markerfacecolor='red',
                  markersize=10, label='Goal'),
        patches.Patch(facecolor='red', alpha=0.6, label='Reserved (next 6 ticks)'),
        plt.Line2D([0], [0], color='blue', linestyle='--', alpha=0.5,
                  linewidth=1.5, label='Planned Path')
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.02, 1),
             fontsize=9, framealpha=0.9)

    ax.set_xticks(range(DIM))
    ax.set_yticks(range(DIM))
    ax.grid(False)

def create_gif(seed=42, max_ticks=400, lookahead_k=6, fps=5):
    """Create an animated GIF of a single simulation run."""
    print("\n" + "="*60)
    print("Creating animated GIF...")
    print("="*60 + "\n")

    random.seed(seed)
    grid = Grid()

    frames = []
    tick = 0
    previous_active_positions = set()

    fig, ax = plt.subplots(figsize=(12, 9), dpi=100)
    # Reserve room for the legend anchored outside the axes.
    fig.subplots_adjust(right=0.78)

    print(f"Seed: {seed}")
    print(f"Max ticks: {max_ticks}")
    print(f"Lookahead: {lookahead_k} ticks")
    print(f"Frame rate: {fps} fps\n")

    while not grid.complete() and tick < max_ticks:
        print(f"Starting tick {tick}")
        # Identify newly activated cars
        current_active_positions = set()
        for r in range(DIM):
            for c in range(DIM):
                if grid.active[r][c]:
                    current_active_positions.add((r, c))

        newly_activated = current_active_positions - previous_active_positions

        # Draw and save frame
        draw_frame(grid, ax, tick, newly_activated, lookahead_k)
        frames.append(_figure_to_rgb_array(fig))

        if (tick + 1) % 50 == 0:
            print(f"  Rendered tick {tick + 1}")

        # Update simulation
        print(f"Updating simulation for tick {tick}")
        grid.updateAll()
        grid.step()
        print(f"Simulation updated. Active cars: {sum(1 for row in grid.active for car in row if car)}")
        previous_active_positions = current_active_positions
        tick += 1

    plt.close(fig)

    # Save as GIF
    print(f"\nTotal frames: {len(frames)}")
    print("Writing GIF file...")

    out_path = PLOTS_DIR / "run_demo.gif"
    imageio.mimsave(out_path, frames, fps=fps, loop=0)

    print("\n" + "="*60)
    print("✓ GIF created successfully!")
    print(f"  Output: {out_path}")
    print(f"  Duration: {len(frames)/fps:.1f} seconds")
    print(f"  Simulation completed in {tick} ticks")
    print("="*60 + "\n")

if __name__ == '__main__':
    # Parameters tuned for PowerPoint presentation
    # Lower fps = slower playback
    create_gif(seed=42, max_ticks=400, lookahead_k=6, fps=2)
