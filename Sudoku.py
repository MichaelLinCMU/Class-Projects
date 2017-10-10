#Michael Lin

from tkinter import *
import random
import copy

"""Occasionally takes a while to run because of the function that makes sure
that the board has a unique solution. This requires a lot of backtracking and
recursion as it has to check all the empty cells multiple times with different
combinations of numbers.
"""

#simple menu splash screen
class MenuScreen(object):
    def __init__(self, width, height):
        self.width, self.height = width, height
    
    def draw(self, canvas):
        width, height = self.width, self.height
        canvas.create_rectangle(0,height/3, width, height*2/3, fill = "black")
        canvas.create_text(width/2, height/2-30, text = "Sudoku", 
                            font = "Copperplate 80 bold", fill = "tomato2")
        canvas.create_text(width/2, height/2+30, 
                            text = "Press space to begin", 
                            font = "Copperplate 40 bold", fill = "dodger blue")

#GameOver screen: only if the user correctly fills the board
class GameOver(object):
    def __init__(self, width, height):
        self.width, self.height = width, height
    
    def draw(self, canvas):
        width, height = self.width, self.height 
        canvas.create_rectangle(0,height/3, width, height*2/3, fill = "black")
        canvas.create_text(width/2, height/2-40, text = "You Win!", 
                            font = "Copperplate 80 bold", fill = "orange red")
        canvas.create_text(width/2, height/2+20, 
                            text = "Press 'r' to restart", 
                            font = "Copperplate 40 bold", fill = "Royalblue1")

#this draws numbers that fall down the screen (aesthetics) for menu/game over
class FallingNumbers(object):

    def __init__(self, x, y, height):
        self.x, self.y = x, y
        self.num = random.randint(1,9) #randomly chooses sudoku digits
        self.height = height

    def move(self):
        self.y+=2
        if self.y == self.height:
            self.y = 0 #wraparound

    def draw(self, canvas):
        canvas.create_text(self.x, self.y, text = self.num, 
                        font = "Courier 30 bold", fill = "black")

#helpScreen is a splash screen that gives the instructions for the users
class HelpScreen(object):

    def __init__(self, width, height):
        self.width, self.height = width, height
        self.instructions = """
1. Fill each 3x3 box with a digit, 1 through 9
2. Each row must have only one of each digit
3. Each column must also contain only one of each digit
4. Press 'd' to decrease the difficulty
5. Press 'r' to restart
6. Click into a cell and press 'o' to return the 
    solution of the cell
7. Click into a cell and type your answer
8. To place a temporary answer, click a cell
    then click on a value in the temp list
9. To erase an answer, click the desired cell and type '0' 
"""

    def draw(self, canvas):
        width, height, size, rows, cols=self.width,self.height,self.width/32,9,9
        canvas.create_rectangle(0,0, width, height, fill = "seagreen2", width=5)
        canvas.create_text(width/2, 40, text = "How To Play", 
                font = "Copperplate 80 bold underline", fill = "dodgerblue3")
        canvas.create_text(50, 70, font = "Helvetica 21", anchor = NW,
                            text = self.instructions)
        canvas.create_text(width/2, height-30, text = "Press space to play", 
                            font = "Copperplate 40 bold", fill = "dodgerblue3")
        for row in range(rows): #makes a mini sudoku board
            for col in range(cols):
                canvas.create_rectangle(width/3+size*row,height*19/30+size*col,
                width/3+size*(row+1), height*19/30+size*(col+1),fill = "khaki1")

#the baord class contains the designs for the game screen  
class Board(object):

    def __init__(self, width, height, margin, rows, cols):
        self.width = width
        self.height = height
        self.margin = margin
        self.rows = rows
        self.cols = cols
        self.cellSize = (self.width-2*self.margin)/self.cols


    def draw(self, canvas):
        m, rows, cols, cell = self.margin, 9,9, self.cellSize
        boardWidth, boardHeight = self.width - 2*m, self.height - 2*m
        width, height = self.width, self.height
        canvas.create_rectangle(0,0, self.width, self.height, fill = "salmon")
        canvas.create_rectangle(m, m, self.width-m, 
                                    self.height-m, fill = "khaki1", width = 4)
        canvas.create_text(self.width/2, m/2, font = "Copperplate 30 bold",
            text = "Click a cell and type your answer!", fill = "blue")
        for row in range(rows): #creating whole board
            for col in range(cols):
                canvas.create_rectangle(m+row*cell,m+col*cell, 
                    m+cell*(row+1), m +cell*(col+1))
        canvas.create_text(width/2, height-25, 
                            text = "Press h to learn how to play", 
                            font = "Copperplate 20 bold", fill = "blue")
        canvas.create_text(width - 25, 90, text = "Temp list",
            font = "Helvetica 10")

#input x and y value and return which cell row and col its in
    def getCell(self, x, y):
        cellRow, cellCol = -1,-1
        margin = self.margin
        cellSize = self.cellSize
        for row in range(self.rows):
            if x > (margin + row*cellSize) and x< (margin+(row+1)*cellSize):
                cellRow = row
        for col in range(self.cols):
            if y > (margin + col*cellSize) and y< (margin+(col+1)*cellSize):
                cellCol = col
        return cellRow, cellCol


#checks to make sure there number doesn't occur more than once in the row
def numRows(board, row, num):
    for col in range(len(board)):
        if board[row][col]==num:
            return False
    return True

#checks to make sure the new number doesn't repeat in the column
def numCols(board, col, num):
    for row in range(len(board[0])):
        if board[row][col]==num:
            return False
    return True

#checks to make sure there number doesn't occur more than once in the box
def numSquare(board, row, col, num):
    startRow, startCol = findBoxStart(row, col)
    for row in range(3):
        for col in range(3):
            if board[startRow + row][startCol + col]==num:
                return False
    return True


#checks whether the move is legal
def isLegal(board, row, col, num):
    if numSquare(board, row, col, num) == False:
        return False
    if numCols(board, col, num) == False:
        return False
    if numRows(board, row, num) == False:
        return False
    #all rows, cols, and 3x3 squares must be legal to return true
    return True

#create a list of random numbers, so the board is different every time
def createRandomNums(board):
    N = len(board)
    numList = list(range(1,len(board)+1))
    #random.shuffle(numList)
    return numList

#given a row and a column, find the start of the box it's in (row and column)
def findBoxStart(row, col):
    startRow = 0
    startCol = 0
    if row >=0 and row <=2: #first major row
        startRow = 0
    elif row >=3 and row <= 5: 
        startRow = 3
    elif row >= 6 and row <=8:
        startRow = 6
    if col >=0 and col <=2: #first major column
        startCol = 0
    elif col >=3 and col <= 5:
        startCol = 3
    elif col >= 6 and col <=8:
        startCol = 6
    return startRow, startCol

#make a 2D board that either returns a full board or None
def makeBoard(board, row, col):
    if (row, col) == (len(board), 0):
        return board
    else:
        L = list(range(1,10))
        random.shuffle(L)
        for num in L:
            if isLegal(board, row, col, num)==False:
                continue
            board[row][col]= num
            if col == len(board)-1:
                newRow = row + 1
            else:
                newRow = row
            newCol= (col+1)%len(board) #if it's at the end of the row, col =0
            result = makeBoard(board, newRow, newCol)
            if result != None:
                return board
    return None

#create a full 9x9 2D list with unique numbers
def createBoard(rows, cols):
    board = []
    temp = []
    for row in range(rows):
        for col in range(cols):
            temp.append(0)
        board.append(temp)
        temp = []
    board = makeBoard(board,0,0)
    if board !=None:
        return board
    else:
        board = createBoard(9,9) 
    return board

#user board is simply a 9x9 2D list filled with 0's
def createUserBoard(rows, cols):
    board = []
    temp = []
    for row in range(rows):
        for col in range(cols):
            temp.append(0)
        board.append(temp)
        temp = []
    return board

#user can input a temporary value into a cell with this
#same functionality createUserBoard, but wanted to distinguish the two
def createTempBoard(rows, cols):
    board = []
    temp = []
    for row in range(rows):
        for col in range(cols):
            temp.append(0)
        board.append(temp)
        temp = []
    return board

#this takes into account the level of difficulty that the user desires
#for a higher level, there will be fewer revealed cells
def adjustUserBoard(board, userBoard, difficulty):
    rows, cols = len(board), len(userBoard)
    easy, medium, hard = 20, 20, 40
    numList = []
    count = 0
    if difficulty == 2:
        for num in range(hard):
            numList.append(random.randint(0,len(board)**2))
    elif difficulty == 1:
        for num in range(medium):
            numList.append(random.randint(0,len(board)**2))
    elif difficulty == 0:
        for num in range(easy):
            numList.append(random.randint(0,len(board)**2))
    for row in range(rows):
        for col in range(cols):
            count+=1
            if count in numList:
                userBoard[row][col]= board[row][col]
    return userBoard

#check inBounds, return True or False
def checkCellInBoard(board, x,y):
    return x>-1 and x <len(board) and y >-1 and y<len(board)

#create temporary choice list which is on the side of the board
def createTempChoices(canvas, data):
    size= data.cellSize*3/4
    startX = data.width-45
    startY = 100
    mid = size/2
    for i in range(0,10):
        canvas.create_rectangle(startX, startY + (i)*size, 
                    startX + size, startY + (i+1)*size, fill = "dodger blue")
    for i in range(0,10):
        canvas.create_text(startX+mid, startY + i*size+mid , text = i)

#briefly flashes blue when you click on it, and then returns the temp value
def fillTemp(canvas, data, x, y):
    startX, startY, size = data.width-45, 100, data.cellSize*3/4
    if x > startX and x <startX + data.cellSize*3/4:
        for i in range(0,10):
            if y < (i+1)*size + startY and y>i*size + startY:
                canvas.create_rectangle(startX,(i*size)+startY, startX+size, 
                                (i+1)*size + startY, fill = "khaki1")
                return i
    return 0

#Indexing the 2D list to find the first instance of a 0
def findFirstZero(board):
    rows = len(board)
    for row in range(rows):
        if int(0) in board[row]:
            return row, board[row].index(0)
            #row and column of the first 0
    return False

#find all occurances of a zero in the board
#used to check board uniqueness
def findAllZeroes(board):
    rows, cols = len(board), len(board[0])
    result = []
    for row in range(rows):
        for col in range(cols):
            if board[row][col]==0:
                result.append((row, col))
                #want tuples of each location of the zero in the baord
    return result

"""this is the step that makes loading the board slightly slow. This function is 
given a filled board and a partially filled board and  makes sure the board
has only one unique solution. If there are multiple values that can be placed
into a cell to make a legal solution, that cell is filled
"""
def uniqueBoard(board, userBoard):
    L = findAllZeroes(userBoard)
    N = len(L)
    random.shuffle(L) #want the cells checked randomly, not just in order
    for num in range(N):
        testBoard = copy.deepcopy(userBoard)
        targetRow, targetCol = L[num]
        for num in range(1,10):
            if num == board[targetRow][targetCol]:
                continue
            testBoard[targetRow][targetCol] = num
            if findAlternateSolution(board, testBoard):
                userBoard[targetRow][targetCol] = board[targetRow][targetCol]
                break
            testBoard = copy.deepcopy(userBoard) 
            #reset testBoard if can't find a solution in the cell
    return userBoard

"""given a filled board and a test board, checks to see if there's a solution
It goes through all the empty cells and uses backtracking to see if there's
a possible solution
"""
def findAlternateSolution(board, userBoard):
    rows, cols = len(board), len(board[0])
    if findFirstZero(userBoard) == False:
        for row in range(rows):
            for col in range(cols):
                num = userBoard[row][col]
                userBoard[row][col] = 0
                if isLegal(userBoard, row, col, num)==False: return False
                else: userBoard[row][col]=num
        return True
    else:
        L = list(range(1,10)) #want to check all the numbers
        row, col = findFirstZero(userBoard)
        for num in L:
            if isLegal(userBoard, row, col, num)==False:
                if num == L[len(L)-1]:
                    userBoard[row][col] = 0
                    return False
                else: continue
            if isLegal(userBoard, row, col, num)==True:
                userBoard[row][col]=num
                result = findAlternateSolution(board, userBoard)
                if result != False: return True
                else: userBoard[row][col]=0
    return False

###############################################################################

#initialize values for game
def init(data):
    print("Loading new board...")
    data.margin, data.rows, data.cols = 50, 9, 9
    data.menu, data.nums = MenuScreen(data.width, data.height), []
    data.board = Board(data.width, data.height,data.margin,data.rows, data.cols)
    data.help = HelpScreen(data.width, data.height)
    data.done = GameOver(data.width, data.height)
    data.helpScreen, data.menuScreen, data.gameScreen = False, True, False
    data.difficulty, data.gameOver = 2, False
    data.timer, data.score, data.menuTimer = 0,0,0
    data.solution, data.userBoard = createBoard(9,9), createUserBoard(9,9)
    data.userBoard=adjustUserBoard(data.solution,data.userBoard,data.difficulty)
    data.userBoard = uniqueBoard(data.solution, data.userBoard) #make unique
    data.cellSize = (data.width-(2*data.margin))/data.cols
    data.numList = ["0","1","2","3","4","5","6","7","8","9"]
    data.tempBoard = createTempBoard(9,9)
    data.selection, data.pastSelection = (-1,-1), (-1,-1)
    print("Enjoy the game!")

#user input to click on cells on temporary values
def mousePressed(canvas,event, data):
    rows, cols = data.selection
    pastR, pastC = data.pastSelection[0], data.pastSelection[1]
    if data.gameScreen == True:
        data.selection = data.board.getCell(event.x, event.y)
        if data.pastSelection[0]!=-1 and data.pastSelection[0]!=-1:
            data.tempBoard[pastR][pastC] = fillTemp(canvas, data, event.x, 
                                                            event.y)
        data.pastSelection = data.selection
        #pastSelection is used in case we decide to place temporary values


#different types of user input
def keyPressed(event, data):
    (rows, cols), num = data.selection, event.keysym
    if event.keysym == "space": #play the game
        data.menuScreen, data.gameScreen, data.helpScreen = False, True, False
    if event.keysym == "h": data.helpScreen, data.gameScreen = True, False
    if event.keysym == "r": init(data)#restart game
    if event.keysym == "d" and data.difficulty >0: #decrease difficulty
        data.difficulty-=1
        adjustUserBoard(data.solution,data.userBoard,data.difficulty)
    if event.keysym in data.numList and rows!= -1 and cols!=-1:
        data.userBoard[rows][cols] = int(num) #place value into cell
    if event.keysym == "Up" and data.selection[1]>0: #move selection box
        data.selection= (data.selection[0],data.selection[1]-1)
    if event.keysym == "Down"and data.selection[1] <data.rows-1:
        data.selection= (data.selection[0],data.selection[1]+1)
    if event.keysym == "Left" and data.selection[0]>0:
        data.selection= (data.selection[0]-1,data.selection[1])
    if event.keysym == "Right"and data.selection[0] <data.cols-1:
        data.selection= (data.selection[0]+1,data.selection[1])
    if checkCellInBoard(data.userBoard, rows,cols):
        if event.keysym == "o": #place solution value
            data.userBoard[rows][cols] = data.solution[rows][cols]

def timerFired(data):
    if not data.gameOver and not data.helpScreen and not data.menuScreen:
        data.timer+=1
    data.menuTimer +=1 #for the falling numbers
    x, y = random.randint(0,data.width), random.randint(0,data.height)
    if data.timer%30 == 0 and data.gameScreen == True: data.score+=1
    if data.helpScreen == True: data.timerDelay = 0
    elif data.menuScreen == True or data.gameOver == True:
        data.timerDelay = 0
        if data.menuTimer%10==0:
            data.nums.append(FallingNumbers(x,y,data.height))
        for num in range(len(data.nums)): 
            data.nums[num].move() #make numbers fall
    checkGameOver(data)

#goes through the board to see if it's complete and everything is legal
def checkGameOver(data):
    if data.menuScreen == False:
        for rows in range(len(data.userBoard)):
            if int("0") in data.userBoard[rows]:
                break
            elif ((rows == len(data.userBoard)-1) and int("0") not 
                                                in data.userBoard[rows]):
                for row in range(len(data.userBoard)):
                    for col in range(len(data.userBoard[0])):
                        num = data.userBoard[row][col]
                        data.userBoard[row][col]=0
                        if not isLegal(data.userBoard,row,col, num):
                            return False
                        else: data.userBoard[row][col]= num
                data.gameOver = True
        if data.gameOver == True: data.timerDelay = 0

#checks to see if a move is legal or not. If so, fill green, otherwise red
def createLegalRectangles(canvas, data):
    m, cell, rows, cols = data.margin, data.cellSize, data.rows, data.cols
    for r in range(rows):
        for c in range(cols):
            num = data.userBoard[r][c]
            #holding the number in memory
            if data.userBoard[r][c]!=0:
                data.userBoard[r][c]=0
                #setting the cell to 0 temporariy to check legality
                if isLegal(data.userBoard, r,c, num):
                    canvas.create_rectangle(m+r*cell, m+c*cell, m+(r+1)*cell,
                            m+(c+1)*cell, fill = "springgreen2") 
                elif not isLegal(data.userBoard, r, c, num):
                    canvas.create_rectangle(m+r*cell, m+c*cell, m+(r+1)*cell,
                                    m+(c+1)*cell, fill = "tomato2") 
                data.userBoard[r][c]=num
                #placing the number back

#draw the game screen that the user plays on
def drawGameScreen(canvas, data):
    m, cell, (row, col) = data.margin, data.cellSize, data.selection
    pastRow, pastCol = data.pastSelection
    if data.gameScreen == True:
        data.board.draw(canvas)
        canvas.create_text(50, data.height-25, anchor = W, 
                text = "Timer: %d" %data.score, font = "Helvetica 15 bold")
        canvas.create_text(data.width-25, data.height-25, anchor = E, 
                text = "Level: %d" %data.difficulty, font = "Helvetica 15 bold")
        createLegalRectangles(canvas, data)
        canvas.create_rectangle(m,m, data.width-m, data.height-m, width = 4)
        if row != -1 and col !=-1: #show which cell you're selecting
            canvas.create_rectangle(m+row*cell, m+col*cell, m+(1+row)*cell,
                    m+(1+col)*cell, fill = "turquoise", width = 2)
        for r in range(data.rows): #user values
            for c in range(data.cols):
                if data.userBoard[r][c]!=0:
                    canvas.create_text(m+r*cell+cell/2, m +c*cell + cell/2, 
                        text = str(data.userBoard[r][c]), font="Helvetica 40")
        for r in range(data.rows): #showing temporary values
            for c in range(data.cols):
                if data.tempBoard[r][c]!=0:
                    canvas.create_text(m+r*cell+cell*3/4, m +c*cell + cell/5, 
                        text = str(data.tempBoard[r][c]), font="Helvetica 10")
        createTempChoices(canvas, data)

#helpCreateGameOverScreen helps draw the screen when the user wins the game
def helpCreateGameOverScreen(canvas, data):
    width, height, rectangles = data.width, data.height, 9
    if data.gameOver == True:
        rHeight = height/rectangles
        for rect in range(rectangles):
            if rect %2 == 0:
                canvas.create_rectangle(0,rHeight*rect, width, rHeight*(rect+1), 
                                                fill = "royalblue1")
            else: canvas.create_rectangle(0,rHeight*rect,width,rHeight*(rect+1), 
                                                fill = "coral1")
        for num in range(len(data.nums)):
            data.nums[num].draw(canvas) #falling numbers
        data.done.draw(canvas) #draw gameOver class draw function
        canvas.create_text(data.width/2, data.height/2 +60, 
            text = "Final Time: %d minutes, %d seconds" %(data.score//60, 
                                                    data.score%60), 
            font = "CopperPlate 20", fill = "coral1") #score

def redrawAll(canvas, data):
    width, height, rectangles, s = data.width, data.height, 9, data.width/32
    m, cell, (row, col) = data.margin, data.cellSize, data.selection
    rows, cols, boardWidth = 9,9, data.width - 2*data.margin
    if data.helpScreen == True: 
        data.help.draw(canvas)
        for row in range(data.rows):
            for col in range(data.cols):
                if data.userBoard[row][col]!=0: #mimic the sudoku board
                    canvas.create_rectangle(width/3+s*row,height*19/30+s*col,
                width/3+s*(row+1), height*19/30+s*(col+1),fill = "brown2")
    if data.menuScreen == True:
        canvas.create_rectangle(0,0,data.width,data.height,fill ="dodger blue")
        for num in range(len(data.nums)):
            data.nums[num].draw(canvas) #falling numbers
        data.menu.draw(canvas)
    if data.gameScreen == True:
        drawGameScreen(canvas, data)
        for row in range(1, rows): #creating bolded lines to show rows
            position = m + row*boardWidth/cols
            if row % (rows**.5) ==0: 
                canvas.create_line(position,m, position, height-m, width = 4)
        for col in range(1, cols): #creating bolded lines to show columns
            position = m + col*boardWidth/rows
            if col % (cols**.5) ==0: 
                canvas.create_line(m, position, width-m, position, width = 4)
    helpCreateGameOverScreen(canvas, data)
    
        
def run(width=600, height=600): 
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(canvas, event, data)
        canvas.update()
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
        
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    init(data)
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run()

############################Test Functions######################################
def testFindAlternateSolutions():
    print("Testing Find Alternate Solutions...", end = "")
    assert(findAlternateSolution(createUserBoard(9,9), createBoard(9,9))==True)
    print("Passed!")

def testCreateUserBoard():
    print("Testing Create User Board...", end = "")
    assert(createUserBoard(9,9) == [[0]*9]*9)
    print("Passed!")

def testFindBoxStart():
    print("Testing Find Box Start...", end = "")
    assert(findBoxStart(3, 2)== (3,0))
    assert(findBoxStart(3, 8)==(3,6))
    assert(findBoxStart(9, 7)==(0,6))
    print("Passed!")

def testFindAllZeroes():
    print("Testing Find All Zeroes...", end = "")
    assert(findAllZeroes(createBoard(9,9))==[])
    print("Passed!")

board = [[2, 8, 0, 7, 6, 5, 3, 1, 4], 
[4, 3, 5, 8, 2, 1, 0, 6, 7], 
[6, 7, 1, 9, 4, 3, 8, 2, 5], 
[3, 4, 2, 1, 5, 8, 7, 9, 6], 
[7, 5, 8, 2, 9, 6, 1, 4, 3], 
[9, 1, 6, 4, 3, 7, 2, 5, 8], 
[1, 6, 3, 5, 8, 9, 4, 7, 2], 
[5, 9, 4, 3, 7, 2, 6, 8, 1], 
[8, 2, 7, 6, 1, 4, 5, 3, 9]]

def testNumRows():
    print("Testing numRows...", end = "")
    assert(numRows(board, 0, 9)==True)
    assert(numCols(board, 2, 8)==False)
    print("Passed!")

def testNumCols():
    print("Testing numCols...", end = "")
    assert(numCols(board, 2, 9)==True)
    assert(numCols(board, 2, 8)==False)
    print("Passed!")

def testNumSquare():
    print("Testing numSquare...", end = "")
    assert(numSquare(board, 0, 2, 9)==True)
    assert(numSquare(board, 0, 2, 8)==False)
    print("Passed!")

def testCheckCellInBoard():
    print("Testing Check Cell in Board...", end = "")
    assert(checkCellInBoard(createUserBoard(9,9), 3,3)==True)
    assert(checkCellInBoard(createUserBoard(9,9), 9,-1)==False)
    assert(checkCellInBoard(createUserBoard(9,9), 9,0)==False)
    print("Passed!")

def testAll():
    testFindAlternateSolutions()
    testCreateUserBoard()
    testFindBoxStart()
    testFindAllZeroes()
    testNumRows()
    testNumCols()
    testNumSquare()
    testCheckCellInBoard()

#testAll()

