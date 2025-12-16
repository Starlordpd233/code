from CarSimTools import *
import sys

def test():
    grid = Grid()
    max_ticks = 30
    ticks = 0
    while not grid.complete() and ticks < max_ticks:
        print(f"--- Tick {ticks} (grid.global_tick={grid.global_tick}) ---")
        grid.updateAll()
        grid.step()
        print(grid)
        ticks += 1
        # Check for any obvious issues
        for r in range(DIM):
            for c in range(DIM):
                if grid.active[r][c]:
                    car = grid.active[r][c]
                    # ensure direction_sequence exists
                    if not hasattr(car, 'direction_sequence'):
                        print(f"ERROR: car at ({r},{c}) missing direction_sequence")
                        return
                    if not hasattr(car, 'activation_tick'):
                        print(f"ERROR: car at ({r},{c}) missing activation_tick")
                        return
                    # ensure direction matches direction_sequence
                    ticks_active = grid.global_tick - car.activation_tick
                    if ticks_active < len(car.direction_sequence):
                        expected_dir = car.direction_sequence[ticks_active]
                        if car.direction != expected_dir:
                            print(f"WARNING: car at ({r},{c}) direction mismatch: {car.direction} vs expected {expected_dir}")
        # Count active cars
        active_count = sum(1 for row in grid.active for car in row if car)
        print(f"Active cars: {active_count}")
    print(f"Test finished after {ticks} ticks")
    print(f"Remaining inactive cars: {sum(len(grid.inactive[r][c]) for r in range(DIM) for c in range(DIM))}")

if __name__ == "__main__":
    test()