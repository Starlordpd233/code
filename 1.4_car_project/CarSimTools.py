import random

DIM = 10

class Location:
    def __init__(self, r, c):
        '''treat these as accessible but immutable'''
        self.row = r
        self.col = c

    def locInDirection(self, dir):
        if dir == 0 and self.row != 0:             #up
            return Location(self.row-1, self.col)
        elif dir == 1 and self.row != DIM-1:       #down
            return Location(self.row+1, self.col)
        elif dir == 2 and self.col != 0:           #left
            return Location(self.row, self.col-1)
        elif dir == 3 and self.col != DIM-1:       #right
            return Location(self.row, self.col+1)
        return None; #can't go off the grid because it'll return None

    def __eq__(self, other):
        if not other:
            return False
        return self.row == other.row and self.col == other.col

    def __str__(self):
        return f'({self.row}, {self.col})'

class Car:
    def __init__(self, startR, startC):
        self.currentLoc = Location(startR, startC)
        self.goalLoc = Location(random.randrange(0, DIM), random.randrange(0, DIM))
        self.activation_tick = 0
        self.direction_sequence = []

        #make sure the car's goal isn't its starting location
        while self.currentLoc == self.goalLoc:
            self.goalLoc = Location(random.randrange(0, DIM), random.randrange(0, DIM))
        self.direction = 0;
        self.active = False;

    def update(self):
        if self.active:
            self.currentLoc = self.currentLoc.locInDirection(self.direction);
        return self.currentLoc;
    
    def get_position(self) -> Location:
        return self.currentLoc
    
    def get_goal(self) -> Location:
        return self.goalLoc

    def remove(self):
        self.active = False

    def activate(self):
        self.active = True

    def setDirection(self, dir):
        self.direction = dir

    def __str__(self):
        if self.direction == 0:
            return "^"
        elif self.direction == 1:
            return "v"
        elif self.direction == 2:
            return "<";
        elif self.direction == 3:
            return ">";

class Grid:
    def __init__(self):
        self.inactive = [[[] for r in range(DIM)] for c in range(DIM)]
        self.active = [[None for r in range(DIM)] for c in range(DIM)]
        self.global_tick = 0

        for r in range(DIM):
            for c in range(DIM):
                for i in range(5):
                    self.inactive[r][c].append(Car(r, c))

    def peek(self, loc):
        '''gives access to the next car at a given Location'''
        if len(self.inactive[loc.row][loc.col]) == 0:
            return None;
        else:
            return self.inactive[loc.row][loc.col][0]

    def is_empty(self): #for naive implementation
        for row in self.active:
            for car in row:
                if car:
                    return False
        return True

    def activateCar(self, loc):
        '''
        Activates the first car at location loc by bringing it onto the
        active grid.
        Precondition: loc != None
        '''
        if self.active[loc.row][loc.col] != None:
            print(f'Car brought on at occupied position {loc}')
            exit()
        if len(self.inactive[loc.row][loc.col]) == 0:
            print(f'No car to bring on at position {loc}')
            exit()

        self.active[loc.row][loc.col] = self.inactive[loc.row][loc.col].pop(0)
        self.active[loc.row][loc.col].activate()


    def compute_direction_sequence(self, start_row, start_col, goal_row, goal_col):
        
        #creates the future direction sequence of a car. Horizontal first routing.
        # ex. [3, 3, 3, 1, 1, 1, 1]
        direction_sequence = []

        while start_col != goal_col:
            if goal_col > start_col:
                direction_sequence.append(3)
                start_col += 1
            else:
                direction_sequence.append(2)
                start_col -= 1

            
            
        while start_row != goal_row:
            if goal_row > start_row:
                direction_sequence.append(1)
                start_row += 1
            else:
                direction_sequence.append(0)
                start_row -= 1

        return direction_sequence
    
    def compute_future_path(self, start_row, start_col, goal_row, goal_col, start_tick=None):
        
        #creates a list of tuples storing the future path of a car: [`(col, row, tick)
        
        if start_tick is None:
            start_tick = self.global_tick

        future_path = []
        current_col = start_col
        current_row = start_row
        
        tick = start_tick

        while current_col != goal_col:
            tick += 1
            if goal_col > current_col:
                current_col += 1
            else:
                current_col -= 1
            
            future_path.append((current_row, current_col, tick))
            
        
        while current_row != goal_row:
            tick += 1
            if goal_row > current_row:
                current_row += 1
            else:
                current_row -= 1
            future_path.append((current_row, current_col, tick))

        return future_path


    '''TO BE IMPLEMENTED:
       1) Bring on any cars that should come onto the grid
       2) Turn any cars that should be turned
       **You may not alter inactive or active in any other way**
    '''
    '''
    def updateAll(self):
        if self.is_empty(): #for naive implementation
            done = False
            for r in range(len(self.active)):
                for c in range(len(self.active[r])):
                    loc = Location(r,c)
                    if self.peek(loc):
                        self.activateCar(loc)
                        done = True
                        break
                if done:
                    break
        
        for r in range(len(self.active)):
                for c in range(len(self.active[r])):
                    car = self.active[r][c]
                    if car:
                        #tell the car to point the right way#################################
                        pass                     
    '''

    def updateAll(self):

        #set the next direction for each active car
        for row in self.active:
            for car in row:
                if car:
                    ticks_active = self.global_tick - car.activation_tick
                    if ticks_active < len(car.direction_sequence):
                        direction = car.direction_sequence[ticks_active]
                        car.setDirection(direction)

        #Now look up all the future positions of each active car
        reserved_cells_with_time = set()

        for row in self.active:
            for car in row:
                if car:
                    current_row = car.get_position().row
                    current_col = car.get_position().col

                    future_path = self.compute_future_path(current_row, current_col, car.get_goal().row, car.get_goal().col)

                    for tup in future_path:
                        reserved_cells_with_time.add(tup) 

        #Now, we will gather potential candidate cars for activation. There is not a maximum number. 

        candidates = []

        for r in range(DIM):
            for c in range(DIM):
                if self.active[r][c] is None:
                    loc = Location(r, c)
                    car = self.peek(loc)

                    if car is not None:
                        goal_row = car.get_goal().row
                        goal_col = car.get_goal().col

                        relative_path = self.compute_future_path(r, c, goal_row, goal_col, start_tick=0)

                        direction_sequence = self.compute_direction_sequence(r, c, goal_row, goal_col)

                        path_length = len(relative_path) #number of moves needed

                        candidates.append({
                            'car': car,
                            'start_row': r,
                            'start_col': c,
                            'relative_path': relative_path,
                            'direction_sequence': direction_sequence,
                            'path_length': path_length,
                        })

        #Now, sort the candidates based on path length and position
        candidates.sort(key=lambda x: (x['path_length'], x['start_row'], x['start_col']))




        #Now, we will select the candidates, following a rule of being greedy in  the sense that we will select candidates until there is a collision detected in the reserved cells.

        selected_cars = []

        for candidate in candidates:

            #initiate the global path that stores all future used cells
            global_path = [(row, col, tick + self.global_tick) for (row, col, tick) in candidate['relative_path']]

            has_conflict = False
            for cell in global_path:
                if cell in reserved_cells_with_time:
                    has_conflict = True
                    break
            
            if not has_conflict:
                selected_cars.append(candidate)

                for cell in global_path:
                    reserved_cells_with_time.add(cell)

                car = candidate['car']
                car.direction_sequence = candidate['direction_sequence']
                car.activation_tick = self.global_tick
                car.setDirection(car.direction_sequence[0])
                self.activateCar(Location(candidate['start_row'], candidate['start_col']))

        self.global_tick += 1




    def step(self):
        newspots = [[None for r in range(DIM)] for c in range(DIM)]

        for row in self.active:
            for car in row:
                if car != None:
                    loc = car.update()
                    if loc == None:
                        print(f'CAR HIT THE EDGE at {loc}');
                        exit()
                    elif loc == car.goalLoc:
                        car.remove()
                    elif newspots[loc.row][loc.col] != None:
                        print(f'COLLISION at {loc}!');
                        exit()
                    else:
                        newspots[loc.row][loc.col] = car;

        self.active = newspots;

    def complete(self):
        '''returns True if all cars have reached their goal, false otherwise'''
        for row in self.inactive:
            for listy in row:
                if len(listy) > 0:
                    return False

        for row in self.active:
            for car in row:
                if car != None:
                    return False

        return True

    def __str__(self):
        ret = ''
        for i in range(DIM*2+1):
            ret += '-'
        ret += '\n';

        for i in range(DIM):
            ret += '|'

            for j in range(DIM):
                if self.active[i][j]:
                    ret += str(self.active[i][j])
                else:
                    ret += '_'
                ret += '|'
            ret += '\n'
        ret += '\n\n'

        return ret

