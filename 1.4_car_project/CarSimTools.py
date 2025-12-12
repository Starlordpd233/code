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

    '''TO BE IMPLEMENTED:
       1) Bring on any cars that should come onto the grid
       2) Turn any cars that should be turned
       **You may not alter inactive or active in any other way**
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


car = Car(2,3)

print(car.direction)