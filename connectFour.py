"""
Gameplan in a multiline comment (this will be read, but then ignored because it isn't assigned anywhere)

A simple grid of rows and columns that can vary (minimum of whatever "connect n" is)
There will be two players and a board to contain all the moves

The entire window is filled with a grey color, and each square is drawn with a lighter grey.
Then for each spot, draw a circle with the player color. If None, draw grey.
This draw function should also take in as an argument if a current player is active
If it is active, than at the end of everything, draw a grey outline along the column of the mouse

The inputs are gathered by each player as a seperate loop to check where the player clicks their mouse
Make a grey outline in whichever column the mouse is in with the player color 
There will also be a "get lowest square" function inside the board
Whenever the player clicks their mouse, check which column it is and make the move

Whenever a player makes a move, let's first check if there is a four in a row
Let's have a function that returns a list of the diagonals of the move
Then, a seperate function that checks if there is four in a row along any list with the given color/name
If there is a match, return true. If not, continue with the next player gathering their move
We also need to check if the entire board is full, and therefore a draw

I f:d up the rows and columns, so the mouse checks which row instead
"""

import pygame
import random

class Player():
     def __init__(self, color, name):
          self.color = color
          self.name = name
          self.greyColor = list(map(lambda z: z//4 + 120, self.color)) # Change this for a nicer color

     def turn(self, game):
          # This function should return the position of the player's move.
          # This should also call the games draw function with the active player
          turn_running = True
          while turn_running:
               for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                         pygame.quit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                         row = game.getMouseRow(pygame.mouse.get_pos()[0])
                         column = game.getTopPos(row)

                         if row < 0 or row > game.rows-1 or column < 0 or column > game.columns-1:
                              # This is out of bounds
                              continue
                         
                         return (row, column)
               
               game.draw(active_player=self)

     
class Board():
     def __init__(self, rows, columns, Player1, Player2, nInRow=4, squareSize=100, squarePercentage=90, circlePercentage=80):
          self.rows = rows
          self.columns = columns
          self.squareSize = squareSize
          self.squarePercentage = squarePercentage / 100

          self.windowSize = (squareSize*rows, squareSize*columns)
          self.circleRadius = squareSize * circlePercentage // 200
          self.nInRow = nInRow

          self.darkGrey = (100, 100, 100)
          self.lightGrey = (150, 150, 150)

          pygame.init()
          self.screen = pygame.display.set_mode(self.windowSize)
          self.winnerFont = pygame.font.Font("freesansbold.ttf", 64)
          self.infoFont = pygame.font.Font("freesansbold.ttf", 16)
          self.game_init(Player1, Player2)

     def game_init(self, Player1, Player2):
          self.board = [[None for _ in range(self.columns)] for _ in range(self.rows)]
          self.Player1 = Player1
          self.Player2 = Player2
          self.winner = None

     def initPlayers(self):
          self.currentPlayer = self.Player1
          self.otherPlayer = self.Player2

          # self.currentPlayer = random.choice([self.Player1, self.Player2])
          # self.otherPlayer = list(filter(lambda z: z != self.currentPlayer, [self.Player1, self.Player2]))[0]

     def draw(self, active_player=False):
          self.screen.fill(self.darkGrey)
          for row in range(self.rows):
               for column in range(self.columns):
                    # First we draw the squares on each spot
                    pygame.draw.rect(self.screen, self.lightGrey, self.getBoardRect(row, column))
                    # Now the inner dark circles
                    if self.board[row][column] == None:
                         pygame.draw.circle(self.screen, self.darkGrey, self.getBlockCenter(row, column), self.circleRadius)
                    # For all spots that have some data (player), draw a circle with that player's color
                    else:
                         pygame.draw.circle(self.screen, self.board[row][column].color, self.getBlockCenter(row, column), self.circleRadius)
                    
          # Now we need to add the grey outline
          if active_player:
               row = self.getMouseRow(pygame.mouse.get_pos()[0])
               if not (row < 0 or row > self.rows - 1):
                    column = self.getTopPos(row)

                    if not column < 0: # Check if this is out of bounds
                         color = active_player.greyColor
                         pygame.draw.circle(self.screen, color, self.getBlockCenter(row, column), self.circleRadius)
          
          pygame.display.update()
                    

     def getBlockCenter(self, row, column):
          return (row*self.squareSize + self.squareSize//2, column*self.squareSize + self.squareSize//2)

     def getBoardRect(self, row, column):
          # First, the size of the square
          rectSize = self.squareSize * self.squarePercentage
          # Then, calculate the center for the curent block we're in
          blockCenter = self.getBlockCenter(row, column)
          # Now, create the rectangel with the top-left corner
          return pygame.Rect(blockCenter[0] - rectSize//2, blockCenter[1] - rectSize//2, rectSize, rectSize)

     def alternatePlayers(self):
          placeholder = self.otherPlayer
          self.otherPlayer = self.currentPlayer
          self.currentPlayer = placeholder

     def getTopPos(self, row):
          for i in range(self.columns):
               column = self.columns-1 - i
               if self.board[row][column] is None:
                    return column
          # If we are here, that means this entire row is filled
          return -1

     def getMouseRow(self, mousePositionX):
          return mousePositionX // self.squareSize

     def checkList(self, squareList, nInRow):
          if len(squareList) < nInRow:
               return False # There just is no way

          for base in range(len(squareList) - nInRow + 1): # Check combination of "in a row" that does not extend beyond the list
               if squareList[base : base + nInRow].count(self.currentPlayer) == nInRow: # Since the length of this is nInRow, taking the count is checking if everything is the player value
                    return True
          return False
     
     def getDiagonal(self, position, direction):
          change = 1 if direction == "left" else -1

          baseRow = position[0]
          baseCol = position[1]
          while True:
               # Go back one step left/right and up to find the base
               if baseRow - change < 0 or baseRow - change > self.rows-1 or baseCol-1 < 0:
                    # This is the spot. If we go further, then we're out of bounds
                    break
               baseRow -= change
               baseCol -= 1
          
          diagonalList = []
          while True:
               # Now go in a diagonal as far as we can until we hit the edge
               diagonalList.append((baseRow, baseCol))
               baseRow += change
               baseCol += 1
               if baseRow < 0 or baseRow > self.rows-1 or baseCol > self.columns-1:
                    break
          
          # Now we need to take this list and convert it into the data on the board
          return list(map(lambda z: self.board[z[0]][z[1]], diagonalList))
     
     def full_board(self):
          for row in range(self.rows):
               for col in range(self.columns):
                    if self.board[row][col] is None:
                         return False
          return True

     def checkWin(self, position, nInRow):
          

          rowList = [self.board[position[0]][column] for column in range(self.columns)]
          columnList = [self.board[row][position[1]] for row in range(self.rows)]
          diagonalRight = self.getDiagonal(position, "right")
          diagonalLeft = self.getDiagonal(position, "left")

          if self.checkList(rowList, nInRow) or self.checkList(columnList, nInRow) or self.checkList(diagonalRight, nInRow) or self.checkList(diagonalLeft, nInRow):
               return True
          elif self.full_board():
               return True
          else:
               return False
               

     def gameEnd(self):
          # Do the fonts and do the player names
          winnerText = self.winnerFont.render(f"{self.winner.name} Wins!", True, (0, 0, 0))
          infoText = self.infoFont.render("Press BACKSPACE to quit, or press P to play again", True, (0, 0, 0))
          self.screen.blit(winnerText, (self.windowSize[0]//2 - 200, self.windowSize[1]//2))
          self.screen.blit(infoText, (self.windowSize[0]//2 - 200, self.windowSize[1]//2 + 100))

          pygame.display.update()
          # Now loop through the inputs until the player either quits or presses p to play again
          end_running = True
          while end_running:
               for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                         end_running = False
                    if event.type == pygame.KEYDOWN:
                         if event.key == pygame.K_p:
                              end_running = False
                              self.game_init(self.Player1, self.Player2)
                              self.play()
                         if event.key == pygame.K_BACKSPACE:
                              end_running = False

     def play(self):
          game_running = True
          self.initPlayers()
          self.draw()

          while game_running:
               for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                         game_running = False
               
               currentPlayer_move = self.currentPlayer.turn(self)

               self.board[currentPlayer_move[0]][currentPlayer_move[1]] = self.currentPlayer
               self.draw()

               if self.checkWin(currentPlayer_move, self.nInRow):
                    self.winner = self.currentPlayer
                    game_running = False
                    self.gameEnd()
                    
               
               self.alternatePlayers()
               


if __name__ == "__main__":
     Game = Board(7, 6, Player((255, 0, 0), "Silas"), Player((255, 255, 0), "Pontus"), squareSize=120, squarePercentage=95, nInRow=4)
     Game.play()