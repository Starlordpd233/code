from CarSimTools import *
import os
import time

def main():
    grid = Grid()
    ticks = 0

    while not grid.complete():
    #for i in range(10):
        os.system('cls' if os.name=='nt' else 'clear')


        grid.updateAll()
        grid.step()
        print(grid)

        time.sleep(0.05)    #alter this number fo speed up your simulation
        ticks += 1

    print(f'Routing complete! {ticks} ticks.')

main()
