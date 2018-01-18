'''
Created on Jan 2, 2018

@author: Nick
'''
from pip._vendor.distlib.compat import raw_input
import random
import sqlite3

'''First, for machine learning to work, we must have a database
that we are connecting to in order to store the data. For this reason
we use conn as our connecting variable and cur as our databases cursor
variable.'''
conn = sqlite3.connect('tictactoe.sqlite')
cur = conn.cursor()

'''The following cursor execution will allow me to both drop and
create any tables necessary in the database. However, since we only
have one table, the dropping is primarily for testing purposes. Once
the whole script is fully functional it will not be needed.'''

cur.executescript('''

CREATE TABLE IF NOT EXISTS BoardState(
    Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    pos0 VARCHAR(1),
    pos1 VARCHAR(1),
    pos2 VARCHAR(1),
    pos3 VARCHAR(1),
    pos4 VARCHAR(1),
    pos5 VARCHAR(1),
    pos6 VARCHAR(1),
    pos7 VARCHAR(1),
    pos8 VARCHAR(1),
    Xs INTEGER,
    Os INTEGER,
    TotalXO INTEGER,
    Empty INTEGER,
    HomeAway VARCHAR(4),
    Comp VARCHAR(1),
    Player VARCHAR(1),
    Next_Move INTEGER,
    Decision VARCHAR(1)
);
''')

#to keep track of the state of the previous board, we need a variable that
#holds the state of said previous board.
prevboard = [' ']*9

'''create turn variable to keep track of whose turn it is.
    0 = player, 1 = computer, -1 = neither
'''
turn = -1

#make a winner variable that can be accessed and saved (machine learning)
win = -2

#create two variables to see who went first, home, and
#who went second, away, incase machine learning is desired
home = 0
away = 0

#these two variables will store a sting to tell the computer if the computer or
#player is home or away.
cha = ""
pha = ""

#this variable will tell the computer whether or not the ai is training against
#another ai that does machine learning
machineL = False

#boolean for if the game is done, activate saving of information, machine learning
done = False

#create a boolean to see if the player would like a rematch or not
rematch = True

#creates a variable to hold the player's symbol, 'X' or 'O'
p1Symbol = ''

#creates a variable to hold the computer's symbol, 'X' or 'O'
compSymbol = ''

#function to draw the board with the updated moves.
def drawB(board):
    print ("   |   |   ")
    print(" " + board[0] + " | " + board[1] + " | " + board[2])
    print("   |   |   ")
    print("---+---+---")
    print("   |   |   ")
    print(" " + board[3] + " | " + board[4] + " | " + board[5])
    print("   |   |   ")
    print("---+---+---")
    print("   |   |   ")
    print(" " + board[6] + " | " + board[7] + " | " + board[8])
    print("   |   |   ")

#function to allow the player to choose if they would like to be X or O
def XorO():
    #must tell the function that these variables are global variables.
    global p1Symbol, compSymbol
    #choice will represent what the player chooses to be
    choice = ''
    #while choice is not equal to either an X or an O it will
    #keep prompting the user for an X or an O
    while not(choice == "X" or choice == "O"):
        choice = str(raw_input("Would you like to be X or O? ").upper())
    #if the player chose to be X
    if(choice == "X"):
        #sets the player's symbol to X and the computer's to O
        p1Symbol = "X"
        compSymbol = "O"
    else:
        #sets the player's symbol to O and the computer's to X
        p1Symbol = "O"
        compSymbol = "X"    

#function to determine who goes first, 0 for player, 1 for computer
def firstTurn():
    #must tell function to use the global variables turn,
    #home and away.
    global turn, home, away, pha, cha
    #set a variable to a random into, 0 or 1
    first = random.randint(0,1)
    #if it is 0 the player is home and goes first.
    if(first == 0):
        turn, home = [0,0]
        away = 1
        pha ="Home"
        cha = "Away"
        print("The player will go first")
    #if it is 1 the computer is home and goes first.
    else:
        turn, home = [1,1]
        away = 0
        pha = "Away"
        cha = "Home"
        print("The computer will go first.")

#If the computer is not training, this function resets the board if the player
#wants to play another game. If it is training, the player and computer symbols
#are pre-set.
def gameSetup(t):
    global p1Symbol, compSymbol
    if(t =="no"):
        XorO()
    else:
        p1Symbol = "X"
        compSymbol = "O"
    firstTurn()

'''this function gets the players move. To do so, it checks to see if
    1. it is the players turn
    2. if the slot they chose is on the board
    3. if the slot they chose is available'''
def getMove():
    #must tell the function to use the global variables for turn
    global turn
    if (turn != 0):
        print("DEBUG: It isn't the player's turn yet!");
        return None;
    #create a variable to hold the slot the player wants to move in
    slot = -1
    #while statement to make sure the spot the player chose is both legal
    #and available.
    while(slot<0 or slot > 8):
        slot = int(raw_input("What slot do you want?  The slots are numbers 0-8 (across the rows from top-left). "))
        if(slot<0 or slot>8):
            print("Please select a different slot. ")
        elif(not freeSpace(brd, int(slot))):
            print("Please select a different slot. ")
            slot =-1;
        else:
            return slot;

def changeTurn():
    #must tell the function to use the global variable turn
    global turn
    if(turn == 0):
        turn = 1
        print("Computer's Turn")
    else:
        turn = 0
        print("Player's Turn")

'''This function  takes three things:
    1. The board
    2. The player's move
    3. The player's symbol, X or O 
it will then apply their move to the board'''
def applyMove(board, move, XO):
    board[move]=XO
    
#function to determine if the space on the board is free.
def freeSpace(board, move):
    if(board[move]==' '):
        return True
    else:
        if(turn == 0 and train == "no"):
            print("That space is already taken.")
        return False

'''checks to see whether the current turn is home's turn
    away's turn'''
def homeOrAway():
    #must tell the function to use the global variables for turn,
    #home and away
    global turn, home, away
    if(turn == home):
        return home
    else:
        return away

'''This function checks all possible combinations to see if there
    is a winner. If there is a winner, it will call the home or away
    function to see if the winner is home or away and mark the game
    as completed'''
def winner(board):
    #have to tell the function to use global variables not create its own.
    global done, win
    #Check if there is a winner along the rows
    r = 0
    while(r<8):
        m = board[r];
        if (m != ' ' and m == board[r+1] and m == board[r+2]):
            win = homeOrAway()
            done = True
            return True
        r+=3
        
    
    c = 0
    #Check if there is a winner along the cols
    while(c<3):
        m = board[c]
        if (m != ' ' and m == board[c+3] and m == board[c+6]):
            win = homeOrAway()
            done = True
            return True
        c+=1
    

    #What about the diagonals?
    m = board[4]
    if (m != ' ' and ((m == board[0] and m == board[8]) or
                       (m == board[2] and m == board[6]))):
        win = homeOrAway()
        done = True
        return True

    #No winner - but is it a tie?  Could just count number of moves...
    done = False
    for i in board:
        if (i == ' '):
            return False;  #Not done yet...

    #It is a tie...
    done = True;
    win = -1;
    return True;  # All spots are taken

#create a function to ask the player if they would like a rematch
def tryAgain():
    #must tell the function that both rematch and done are global varaibels.
    global rematch, done
    decision = raw_input("Would you like to play again?").lower()
    while not(decision == "yes" or decision == "no"):
        decision= raw_input("I'm sorry, I didn't catch that. Would you like to try again?").lower()
    if(decision == "yes"):
        rematch = True
        done = False
        
    else:
        rematch = False
    
'''The following function will allow us to take the state of the board
and save it to our database. In order to do this, we need to have:
    1. the board
    2. the home and away variables to tell the computer whether it went first
or second as well as whether the computer is home or away as a string for the Insert
statement we need compha (computer home away).
    3. the computer and player symbols so that the computer knows which symbols
to look at when determining a future move.'''
def saveState(board, home, away, computerL, Pl,compha):
    #will need to use the global variables cur, conn and prevboard
    global cur, conn, prevboard
    #these variables will be used to determine how many x's and o's
    #there are on the board as well as how my empty spaces there are (totE)
    x,o, totE=[0,0,0]
    #this for loop will go through the board and add one if the i is an x,
    #an o or empty to the proper variable.
    for i in board:
        if(i == "X"):
            x+=1
        elif(i == "O"):
            o+=1
        else:
            totE +=1
    #the variable that will tell us how many x's and o's are on the board combined
    tot = x+o
    
    '''after we find t, we then are ready to insert into the table. However, we
    don't want to insert everything so we have to specify which every value expect
    the decision and Next_move variables since those are the only two that are
    unkown.'''
    cur.execute('''INSERT INTO BoardState(pos0, pos1, pos2, pos3, pos4, pos5, pos6,
                    pos7, pos8, Xs, Os, TotalXO, Empty, HomeAway, Comp, Player)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (board[0], board[1],
                    board[2], board[3], board[4], board[5], board[6], board[7], board[8],
                    x, o, tot, totE, compha, computerL, Pl))
    #k symbolizes every space in prevboard and when we are updating prevboard to be board,
    #we will use k to navigate to each space of prevboard.
    k=0
    for b in board: 
        prevboard[k] = b
        k+=1
    #conn.commit allows these actions to be executed.
    conn.commit()

'''The updateDecision function will allow us to update the decision column of the 
    table after the computer wins or loses. To do so, it will check to see if win
    is equal to -1, a tie, 1, the computer won, or 0, the player won. after finding
    this out, it will set outcome to the proper text and an update command will run
    to set Decision, in the BoardState table, to what outcome is. Since we only
    want to set the Decision of the most recent game, we want to look for where
    Decision is equal to null.
'''
def updateDecision(win):
    global machineL
    outcome = "none"
    if(machineL == False and win == -1):
        outcome = "Tie"
        cur.execute('''UPDATE BoardState SET Decision = ? WHERE Decision IS NULL''', (outcome, ))
    elif(machineL == False and win == 1):
        outcome = "Win"
        cur.execute('''UPDATE BoardState SET Decision = ? WHERE Decision IS NULL''', (outcome, ))
    elif(machineL == False and win == 0):
        outcome = "Lose"
        cur.execute('''UPDATE BoardState SET Decision = ? WHERE Decision IS NULL''', (outcome, ))
    elif(machineL == True and win == 1):
        outcome = "Win"
        cur.execute('''UPDATE BoardState SET Decision = ? WHERE Decision IS NULL AND HomeAway = ?''', (outcome,cha, ))
        outcome = "Lose"
        cur.execute('''UPDATE BoardState SET Decision = ? WHERE Decision IS NULL AND HomeAway = ?''', (outcome,pha, ))
    elif(machineL == True and win == 0):
        outcome = "Lose"
        cur.execute('''UPDATE BoardState SET Decision = ? WHERE Decision IS NULL AND HomeAway = ?''', (outcome,cha, ))
        outcome = "Win"
        cur.execute('''UPDATE BoardState SET Decision = ? WHERE Decision IS NULL AND HomeAway = ?''', (outcome,pha, ))    
    elif(machineL == True and win == -1):
        outcome = "Tie"
        cur.execute('''UPDATE BoardState SET Decision = ? WHERE Decision IS NULL AND HomeAway = ?''', (outcome,cha, ))
        cur.execute('''UPDATE BoardState SET Decision = ? WHERE Decision IS NULL AND HomeAway = ?''', (outcome,pha, ))
    conn.commit()

'''The updateNextMove function will allow us to take in the most recent move by
    the computer and apply it to the row that matches the previous board state.
    To do this, we must first find the most recent board state my selecting the
    max ID and then using this id to place the computers move in the correct row.
'''
def updateNextMove(csmove):
    cur.execute('''SELECT MAX(Id) FROM BoardState''')
    #thing is what is going to store our most recent board state's ID.
    thing=cur.fetchone()[0]
    cur.execute('''UPDATE BoardState Set Next_Move = ? WHERE Id = ?''',(csmove, int(thing), ))
    conn.commit()

'''Since the wins and total arrays will not be the same length, the sums function
    will take in four arrays, the moves it made that resulted in a win, the total
    amount of times it has made this move in this situation, the move it made when
    it won in this situation (wnext), and the move it made no matter if it won or
    lost in this situation (tnext). If the move that it has made when it wins
    divided by the total amount of times it has made this move, is greater than
    the saved highest average (this will later be a certain percentage) it will
    return the place I can find this move in the wnext array. However, if no moves
    are above 30%, it will return a -1 which I will use to tell the computer
    to choose a move at random. 
'''
def sums(wins,total, wnext, tnext):
    #q will be the variable to go through the total arrays
    q = 0
    #v will be the variable to go through the win arrays
    v = 0
    #avg will hold the new average of win/total
    avg = 0.0
    #highestavg will hold the highest average of win/total
    highestavg = 0.0
    #placeavg will hold the place at which I can find the highest average in the win
    #array.
    placeavg = 0
    '''the following print statements were used for debugging purposes
    print(wins)
    print (total)
    print(wnext)
    print(tnext)'''
    #while q has not gone through the length of the total array yet...
    while(q<len(total)):
        #for every item in wnext array...
        for n in wnext:
            #if that item is equal to the item at tnext[q]
            if(n == tnext[q]):
                #get the average of the total times the computer won while doing this
                #divided by the total times this move has been made and save it to
                #the avg variable. since the items stored in the arrays are not floats
                #I had to convert one of the arrays to a float so I can get a percent
                avg = (wins[v]/float(total[q]))
                print (avg)
                #if avg is higher than the current highest average...
                if(avg > highestavg):
                    #set highestavg to avg and place avg to v
                    highestavg = avg
                    placeavg = v
            #increment v so the computer has the correct location in the wins array.
            v+=1
        #set v back to 0 so we can search the wins array again.
        v=0
        #add one to q so we can continue to go through the totals array.
        q +=1
    #if the highest average is 0 or greater, return the place I can find this
    #value in the wnext array as long as there is something in the wnext array
    if(highestavg >=.0 and len(wnext)>0):
        #used for debugging
        #print(placeavg)
        return placeavg
    else:
        return -1

#makes a copy of the board, used for the AI that is hard coded
def copyBoard(board):
    cBoard=[]
    for l in board:
        cBoard.append(l)
    return cBoard

'''This function allows for a random move to be selected based on
    moves from a list that can be made on the board this function
    is passed.'''
def chooseRandomMove(board, movesList):
    posMoves=[]
    for p in movesList:
        if(freeSpace(board, p)):
            posMoves.append(p)
    if(len(posMoves) != 0):
        return random.choice(posMoves)
    else:
        return None

'''This function computes the hard coded AI's move that we use to train the AI
    using machine learning.
'''
def compMove(board, compsLetter):
    #Get the other AI's symbol
    if(compsLetter == 'X'):
        player = 'O'
    else:
        player = 'X'
    
    #check to see if the computer can win this turn
    for x in range(0,9):
        copy = copyBoard(board)
        if(freeSpace(copy, x)):
            applyMove(copy, x, compsLetter)
            if(winner(copy)):
                return x
    
    #check to see if the player can win on their next turn.
    for i in range(0,9):
        copy2 = copyBoard(board)
        if(freeSpace(copy2, i)):
            applyMove(copy2, i, player)
            if(winner(copy2)):
                return i
    
    #here, the list we hand it is the list of spaces the AI has to choose from.
    #corners
    compChoice = chooseRandomMove(board, [0,2,6,8])
    if(compChoice!= None):
        return compChoice
    
    #middle
    if(freeSpace(board, 4)):
        return 4
    
    #return a random move from remaining spaces
    compChoice = chooseRandomMove(board, [1,3,5,7])
    if(compChoice!= None):
        return compChoice
    else:
        return winner(board)

'''The compMove2 function will allow me to take in the current board and who
    is home or away and figure out what spaces are open, access the database so the
    computer can see what it did the previous times it was in this situation,
    the amount of times it made that move, how many of those decisions ended
    up in a win, and take those totals to calculate whether or not the computer
    should do that move again. In the end, this will allow me to return what
    move the computer should make next.
''' 
def compMove2(board, ha):
    #we will need the global variables cur and conn for this function
    global cur, conn
    #po will keep the new board in it
    po = []
    #w is the lost of the wins that the computer received after choosing a certain
    #move
    w = []
    #l is not used but is supposed to be the amount of losses received after
    #choosing a certain move.
    l = []
    #tot will be the total number of times that move was made
    tot = []
    #empty will be the spots that the computer has available incase it needs
    #to choose one at random.
    empty =[]
    #nxt will be the list of moves the computer has to use next based off of
    #its wins list.
    nxt = []
    nxt2 = []
    
    #em will be our way of itterating through board to see where the empty
    #spaces are.
    em = 0
    #here I set po equal to board and find the empty spaces in our board.
    for i in board:
        po.append(i)
        if(i == " "):
            empty.append(em)
            #print(em)
        em+=1
    
    #here I execute a select statement to find the total amount of times a move was
    #made
    cur.execute('''SELECT COUNT(*), Next_Move
                    FROM BoardState WHERE pos0= ? AND pos1 = ? AND pos2 = ? AND
                    pos3=? AND pos4=? AND pos5=? AND pos6=? AND pos7 =? AND
                    pos8 = ? AND HomeAway =? AND Next_Move IS NOT NULL
                    GROUP BY Next_Move''',
                    (po[0],po[1],po[2],po[3],po[4],po[5],po[6], po[7],po[8], ha,))
    
    conn.commit()
    numbs = cur.fetchall()
    #here I set the moves to the tot array to be accessed later.
    for i in numbs:
        tot.append(int(i[0]))
        nxt2.append(int(i[1]))
        #numbs = int(cur.fetchone()[0])
    conn.commit()
    
    #here I execute another select statement to show what moves
    #were made that resulted in a win. Even if they don't have a win I include them,
    #these moves are just set to 0
    cur.execute('''SELECT COUNT(*), Next_Move
                    FROM BoardState WHERE pos0= ? AND pos1 = ? AND pos2 = ? AND
                    pos3=? AND pos4=? AND pos5=? AND pos6=? AND pos7 =? AND
                    pos8 = ? AND HomeAway =? AND Decision = "Win"
                    GROUP BY Next_Move
                    ''',(po[0],po[1],po[2],po[3],po[4],
                                                 po[5],po[6], po[7],po[8], ha,))
    
    conn.commit()
    #here I set the moves to the w array to be accessed later and the actual
    #position of that move to the nxt array also to be accesses later.
    wins = cur.fetchall()
    for l in wins:
        #used for debuging
        #print(l)
        w.append(int(l[0]))
        nxt.append(int(l[1]))
    conn.commit()
        
    ''' below is where the losses would have been found and set to the appropriate
    array.
    cur.execute(''SELECT COUNT(*)
                    FROM BoardState WHERE pos0= ? AND pos1 = ? AND pos2 = ? AND
                    pos3=? AND pos4=? AND pos5=? AND pos6=? AND pos7 =? AND
                    pos8 = ? AND HomeAway =? AND Decision = "Lose" GROUP BY Next_Move 
                    HAVING COUNT(*)>=0'',(po[0],po[1],po[2],po[3],po[4],
                                                 po[5],po[6], po[7],po[8], ha,))
    
    loss = int(cur.fetchone())
    while(loss!=None):
        l.append(loss)
        loss = int(cur.fetchone())'''
    #mov will be the output of sum, sum will either output the location of our
    #move in the nxt array or return -1 and in that case the AI will randomly choose
    #its next move.
    mov = sums(w, tot, nxt,nxt2)
    #used for debugging
    #print(mov)
    #if the mov is -1 then we will pick a move at random
    if(mov == -1):
        j= (random.choice(empty))
        while(freeSpace(board, j)==False):
            j=(random.choice(empty))
        return j
    #if the move is not set to None we will return the mov we calculated
    elif (mov != None):
        return nxt[int(mov)]
    #otherwise we will return a random move from the moves we won with.
    else:
        return random.choice(nxt)

'''Below we check to see if the player would like to improve the ai doing
    machine learning. If they do then it will prompt the player for a number
    of games it would like the ai to train for. Otherwise, the player will be
    prompted for the letter they would like to be.
'''
#create a train variable to hold the user's decision on if they would like to train
#the AI or not
train = ""
#if the user's answer is anything besides yes or no it will keep asking if the
#user wants to train the AI
while not(train == "yes" or train == "no"):
    train = str(raw_input("Would you like to train the AI?").lower())
    
if(train == "no"):
    '''Below is the code to execute the game. First we must set up the game by
        calling the game setup function. Then we use a while loop to make the
        game continuously run until there is a winner or there is a tie. After
        we have a winner or a tie, we ask if they would like to play again or not.
        if they do not want to play again then we break the loop.'''
    while(rematch ==True):
        #create/recreate the board
        brd = [' '] *9
        #see if the computer is training and if not then ask the player for X or O
        gameSetup(train)
        #while the game isn't finished
        while(done == False):
            #if it's the players turn
            if(turn == 0):
                '''Draw the board, get the players move, apply it to the board, and
                    see if there is a winner. If not, change the turn to the AI.
                '''
                drawB(brd)
                pmove = getMove()
                applyMove(brd, pmove, p1Symbol)
                if(winner(brd)and win == 0):
                    updateDecision(win)
                    print("You won!")
                    drawB(brd)
                elif(winner(brd) and win ==-1):
                    updateDecision(win)
                    print("It's a Tie!")
                    drawB(brd)
                else:
                    changeTurn()
            #if it's not the players turn
            else:
                '''Draw the board, save the state so the AI can learn, compute
                    the AI's move, apply the move to the board, update the next
                    move column, and then check for a winner. If there is a winner
                    update the decision column for this game, if not, change the turn 
                '''
                drawB(brd)
                saveState(brd, home, away, compSymbol, p1Symbol, cha)
                cmove = compMove2(brd, cha)
                applyMove(brd, cmove, compSymbol)
                updateNextMove(cmove)
                if(winner(brd)and win == 1):
                    print("Oh No! The Computer beat you!")
                    updateDecision(win)
                    drawB(brd)
                elif(winner(brd) and win ==-1):
                    print("It's a Tie!")
                    updateDecision(win)
                    drawB(brd)
                else:
                    changeTurn()
        #see if the user wants to play again.
        tryAgain()
else:   
    '''Below is the code to execute the game and train the machine learning AI.
        First we must set up the game by calling the game setup function. Then
        we use a while loop to make the game continuously run until there is a
        it has played the amount of games the user specifies. If it has reached
        the specified number then it will stop.'''
    #ask the user which AI to train against, hard coded or machine learning
    ml = int(raw_input("Would you like to train against 1.) the hard coded AI or 2.) the machine learning AI?"))
    while not(ml == 1 or ml == 2):
        ml = int(raw_input("I'm sorry, I didn't get that, please enter a 1 for hard coded AI or 2 for machine learning AI."))
    if(ml == 1):
        machineL = False
    else:
        machineL = True
    #ask the user how many games it wants to train the AI for and saves it in a
    #var called num.
    num = int(raw_input("How many games should the AI play?"))
    if(machineL == False):
        #while that variable is above 0
        while(num >0):
            #since we don't have a tryagain function, we need to set done to false.
            done = False
            #create a new board
            brd = [' '] *9
            #preset the symbol variables
            gameSetup(train)
            #while the game is still going
            while(done == False):
                #if it is the hard coded AI's turn
                if(turn == 0):
                    #draw the board, compute the AI's move, apply the move, check
                    #for a winner. If there is a winner then update the decision column
                    #of the table. If there is no winner change turns.
                    #drawB(brd)
                    pmove2 = compMove(brd, p1Symbol)
                    applyMove(brd, pmove2, p1Symbol)
                    if(winner(brd)and win == 0):
                        updateDecision(win)
                        print("You won!")
                        drawB(brd)
                    elif(winner(brd) and win ==-1):
                        updateDecision(win)
                        print("It's a Tie!")
                        drawB(brd)
                    else:
                        changeTurn()
                else:
                    '''If it is the AI's turn that does machine learning, draw the board
                        save the state to the table in the database, compute this AI's move
                        apply that move, update the next move column in the previous row,
                        check for a winner. If there is a winner update the decision
                        column of the table. If there is no winner, change the turn.
                    '''
                    drawB(brd)
                    saveState(brd, home, away, compSymbol, p1Symbol,cha)
                    cmove2 = compMove2(brd, cha)
                    applyMove(brd, cmove2, compSymbol)
                    updateNextMove(cmove2)
                    if(winner(brd)and win == 1):
                        print("Oh No! The Computer beat you!")
                        updateDecision(win)
                        drawB(brd)
                    elif(winner(brd) and win ==-1):
                        print("It's a Tie!")
                        updateDecision(win)
                        drawB(brd)
                    else:
                        changeTurn()
            #subtract one from num so there is no infinite loop.
            num -= 1
    
    '''The code below is simply code that has the machine learning AI play against
        itself when the hard coded AI gets to be too weak of an opponent.
    '''
    if(machineL == True):
        #while that variable is above 0
        while(num >0):
            #since we don't have a tryagain function, we need to set done to false.
            done = False
            #create a new board
            brd = [' '] *9
            #preset the symbol variables
            gameSetup(train)
            #while the game is still going
            while(done == False):
                #if it is the hard coded AI's turn
                if(turn == 0):
                    #draw the board, compute the AI's move, apply the move, check
                    #for a winner. If there is a winner then update the decision column
                    #of the table. If there is no winner change turns.
                    #drawB(brd)
                    saveState(brd, home, away, p1Symbol,compSymbol,pha)
                    pmove2 = compMove2(brd, pha)
                    applyMove(brd, pmove2, p1Symbol)
                    updateNextMove(pmove2)
                    if(winner(brd)and win == 0):
                        updateDecision(win)
                        print("You won!")
                        drawB(brd)
                    elif(winner(brd) and win ==-1):
                        updateDecision(win)
                        print("It's a Tie!")
                        drawB(brd)
                    else:
                        changeTurn()
                else:
                    '''If it is the AI's turn that does machine learning, draw the board
                        save the state to the table in the database, compute this AI's move
                        apply that move, update the next move column in the previous row,
                        check for a winner. If there is a winner update the decision
                        column of the table. If there is no winner, change the turn.
                    '''
                    drawB(brd)
                    saveState(brd, home, away, compSymbol, p1Symbol,cha)
                    cmove2 = compMove2(brd, cha)
                    applyMove(brd, cmove2, compSymbol)
                    updateNextMove(cmove2)
                    if(winner(brd)and win == 1):
                        print("Oh No! The Computer beat you!")
                        updateDecision(win)
                        drawB(brd)
                    elif(winner(brd) and win ==-1):
                        print("It's a Tie!")
                        updateDecision(win)
                        drawB(brd)
                    else:
                        changeTurn()
            #subtract one from num so there is no infinite loop.
            num -= 1