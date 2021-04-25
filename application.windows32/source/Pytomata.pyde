import random

global cellSize, delay, activeRowHeight, lastUpdate
cellSize = 20
delay = 250
activeRowHeight = None
lastUpdate = 0
canUpdate = False
rule = None

def setup():
    fullScreen()
    background(0)

    w = width/cellSize


    global activeRowHeight
    activeRowHeight = int(height/cellSize/3*2)
    max_input = 2**w-1        
    
    try:
        row_config = int(input("Please give a numerical input that represent a {}-bit number (between 0 and {}).\nLeaving this empty will generate a random first row.".format(w, max_input)))
    except ValueError:
        row_config = random.getrandbits(w)
        print("That is not a valid number. Now using {}.".format(row_config))

    start_config = decode_booleans(row_config, w)

    
    try:
        rule_number = int(input("Please enter a cellular automata rule number (between 0 and 255).\nLeaving this empty will generate a random rule."))
    except ValueError:
        rule_number = random.randint(0,255)
        print("That was not a number. Now using Rule #{}.".format(rule_number))
        
    if rule_number > 255:
        rule_number %= rule_number
    
    global rule
    rule = rule_number
    
    try:
        _ = input("The cellular automata will now start.\n\nControls:\nThe zone below the red row is the INPUT ZONE.\nUse LEFT MOUSE to turn on cells in the input zone.\nUse RIGHT MOUSE to turn cells off.\nUse MIDDLE MOUSE to set them to neutral.\nPress SPACEBAR to advance a layer.\nPress ESCAPE to exit.\nEnjoy!")
    except:
        pass
        
    # print("Starting row: {}".format(start_config))
    # print("Rule #: {}".format(rule_number))
    global grid, overlay
    grid = Grid(cellSize, start_row=start_config, rule=rule_number)
    overlay = Overlay(cellSize)
    
    textSize(40)
    
def draw():
    background(255)
    global grid, lastUpdate
    
    grid.show()
    overlay.show()
    if (millis() - lastUpdate > delay):
        canUpdate = True
    
    fill(127, 127)
    text("Rule {}".format(rule), 5, 40)
    
def mousePressed():
    global overlay
    cellX = floor(map(mouseX, 0, width, 0, width/cellSize))
    cellY = floor(map(mouseY, 0, height, 0, height/cellSize))
    if mouseButton == LEFT:
        state = True
    elif mouseButton == RIGHT:
        state = False
    elif mouseButton == CENTER:
        state = None
    else:
        return
    overlay.setCell(cellX, cellY, state)
        
    
def mouseDragged():
    global overlay
    cellX = floor(map(mouseX, 0, width, 0, width/cellSize))
    cellY = floor(map(mouseY, 0, height, 0, height/cellSize))
    if mouseButton == LEFT:
        state = True
    elif mouseButton == RIGHT:
        state = False
    elif mouseButton == CENTER:
        state = None
    else:
        return
    overlay.setCell(cellX, cellY, state)
   
def keyPressed():
    canUpdate = False
    lastUpdate = millis()
    grid.update()
    overlay.update()
        
def input(message=""):
    from javax.swing import JOptionPane
    return JOptionPane.showInputDialog(frame, message)
    
def decode_booleans(intval, bits):
    res = []
    intval_to_bool = format(intval, 'b').zfill(bits)
    print(intval_to_bool)
    for bit in xrange(bits):
        print(intval_to_bool[bit] == '1')
        res.insert(0, intval_to_bool[bit] == '1')
    return res
    
########################################################################################################

class Cell:
    
    def __init__(self, x, y, state, cellSize):
        self.x = x
        self.y = y
        self.cellSize = cellSize
        self.state = state
    
    def show(self, color=None):
        if self.state is not None:
            if color == 'red':
                fill(255, 0, 0)
            elif color == 'green':
                fill(0, 255, 0)
            elif color == 'black':
                fill(0)
                
            noStroke()
            rect(self.x * self.cellSize, self.y * self.cellSize, self.cellSize, self.cellSize)
    
    def setState(self, state):
        self.state = state
        
########################################################################################################

class Grid:
    
    def __init__(self, cellSize, start_row=None, rule=60):
        self.cellSize = cellSize
        self.grid = []
        self.w = width/cellSize
        self.h = height/cellSize
        
        self.rules = Rules(rule)
        
        for y in range(self.h):
            self.grid.append([])
            
            for x in range(self.w):
                state = False
                if y == activeRowHeight-1:
                    if start_row == 'random':
                        state = random(1)<0.5
                        
                    elif start_row is None:
                        state = False
                        
                    else:
                        try:
                            state = start_row[x]
                        except ValueError:
                            print("The config list did not contain just booleans, instead got type {} at index {}.".format(type(start_row[x])), x)
                
                self.grid[y].append(Cell(x=x, y=y, state=state, cellSize=cellSize))
     
    def update(self):
        # Calculate new row
        row = self.grid[activeRowHeight-1]
        overlayRow = overlay.overlay[activeRowHeight-1]
        
        newRow = []
        
        for cell, overlayCell in zip(row, overlayRow):
            if overlayCell.state is not None:
                if overlayCell.state:
                    cell.state = cell.state or overlayCell.state
                else:
                    cell.state = cell.state and overlayCell.state
                
        newRow.append(Cell(x=0, y=activeRowHeight-1, state=self.rules.getNextCellState([False] + [c.state for c in row[0:2]]), cellSize=self.cellSize))
                         
        for x in range(1, self.w-1):
            newRow.append(Cell(x=x, y=activeRowHeight-1, state=self.rules.getNextCellState([c.state for c in row[x-1:x+2]]), cellSize=self.cellSize))
                             
        newRow.append(Cell(x=self.w, y=activeRowHeight-1, state=self.rules.getNextCellState([c.state for c in row[-2:]] +[False]), cellSize=self.cellSize))
        
        # Shift all rows up one.
        for y in range(self.h-1):
            for x in range(self.w):
                self.grid[y][x].state = self.grid[y+1][x].state
                
        self.grid[activeRowHeight-1] = newRow
            
        # self.grid[activeRowHeight] = newRow
        for cell in self.grid[-1]:
            cell.state = False
        
    def show(self):
        for row in self.grid:
            for cell in row:
                if cell.state == True:
                    cell.show(color='black')
                
        stroke(0)
        strokeWeight(1)
        for x in range(0, width, cellSize):
            line(x, 0, x, height)
        
        for y in range(0, height, cellSize):
            line(0, y, width, y)
        
        stroke(255,0,0)
        strokeWeight(2)
        line(0, activeRowHeight*cellSize, width, activeRowHeight*cellSize)
        line(0, (activeRowHeight-1)*cellSize, width, (activeRowHeight-1)*cellSize)
            
    # def setCell(self, cellX, cellY, cellState):
    #     if cellX < 0  or cellY > self.h:
    #         return
    #     try:
    #         self.grid[cellY][cellX].setState(cellState)
    #     except IndexError:
    #         pass
    
########################################################################################################

class Rules:
    
    def __init__(self, rules=None):
        
        
        self.rules = {
        (True,  True,  True):  False,
        (True,  True,  False): True,
        (True,  False, True):  False,
        (True,  False, False): True,
        (False, True,  True):  True,
        (False, True,  False): False,
        (False, False, True):  True,
        (False, False, False): False,
        }
        
        boolean_rule = decode_booleans(rules, 8)
        for one in [False, True]:
            for two in [False, True]:
                for three in [False, True]:
                    i = three + 2*two + 4*one
                    self.rules[(one, two, three)] = boolean_rule[i]
        # # Rules should be a list of eight boolean values, on for each combination.
        # if rules is not None:
        #     if type(rules) != list:
        #         raise Exception("Not a list, instead got type {}".format(type(rules)))
        #     elif len(rules) != 8:
        #         raise Exception("Wrong number of rules. Should be 8, but got {} instead".format(len(rules)))
        #     for key_, state in zip(self.rules.keys(), rules):
        #         self.rules[key_] = state
            
    def getNextCellState(self, cellStates):
        # Cell states should be a list or tuple of three parenting cells to calculate the new cell state
        nextState = self.rules[tuple(cellStates)]
        # print(parents, nextState)
        return nextState
    
class Overlay:
    
    def __init__(self, cellSize):
        self.overlay = []
        self.w = width/cellSize
        self.h = height/cellSize
        self.cellSize = cellSize
        
        for y in range(self.h):
            self.overlay.append([])
            for x in range(self.w):
                self.overlay[y].append(Cell(x, y, None, cellSize))
                
    def setCell(self, cellX, cellY, cellState):
        if cellX < 0  or cellX > self.w or cellY > self.h or cellY < 0 or cellY < activeRowHeight:
            return
        try:
            self.overlay[cellY][cellX].setState(cellState)
        except IndexError:
            pass
        
    def show(self):
        for i, row in enumerate(self.overlay):
            if i <= activeRowHeight-1:
                continue
            for cell in row:
                if cell.state == True:
                    color = 'green'
                elif cell.state == False:
                    color = 'red'
                else:
                    color = None
                cell.show(color)
                
    def update(self):
        # Shift all rows up one.
        for y in range(self.h-1):
            for x in range(self.w):
                self.overlay[y][x].state = self.overlay[y+1][x].state
            
        # self.grid[activeRowHeight] = newRow
        for cell in self.overlay[-1]:
            cell.state = None
        for row in self.overlay[:activeRowHeight-1]:
            for cell in row:
                cell.state = None
