from connectFour import Board, Player
import pygame
from copy import deepcopy
import random

class Ai_player(Player):
     def __init__(self, color, name, depth):
          super().__init__(color, name)
          self.depth = depth
     
     def turn(self, game):
          value, move = self.minimax(game.board, self.depth, self, game)
          pygame.time.delay(1000)
          return move

     def minimax(self, board, depth, player, game, latest_move=None):
          if not latest_move is None:
               if depth <= 0 or game.checkWin(latest_move, game.nInRow):
                    return self.evaluate(board, game, depth), latest_move
          
          if player == self:
               maxEval = float("-inf")
               best_move = None
               for row in self.get_all_rows(board, player, game):
                    move = (row, game.getTopPos(row))
                    board = self.simulate_move(board, move, player, game)
                    evaluation = self.minimax(board, depth-1, game.otherPlayer, game, move)[0]
                    board = self.undo_move(board, move, game)
                    maxEval = max(maxEval, evaluation)
                    if maxEval == evaluation:
                         best_move = move
               
               return maxEval, best_move
          else:
               minEval = float("inf")
               best_move = None
               for row in self.get_all_rows(board, player, game):
                    move = (row, game.getTopPos(row))
                    board = self.simulate_move(board, move, player, game)
                    evaluation = self.minimax(board, depth-1, self, game, move)[0]
                    board = self.undo_move(board, move, game)
                    minEval = min(minEval, evaluation)
                    if minEval == evaluation:
                         best_move = move
               
               return minEval, best_move

     def simulate_move(self, board, move, player, game):
          game.board[move[0]][move[1]] = player
          self.draw_moves(game)

     def undo_move(self, board, move, game):
          game.board[move[0]][move[1]] = None
          # self.draw_moves(game)

     def get_all_rows(self, board, player, game):
          rows = []
          for row in range(game.rows):
               column = game.getTopPos(row)
               if not column < 0:
                    rows.append(row)
          return rows

     def evaluate(self, board, game, depth):
          # This is going to be the hardest part
          # I'm thinking loop through all the diagonals, both left and right of any length bigger than 2
          # Then all the columns, which are easy
          # Then all the rows, which is easy
          # Give a sublist of all these lists of length nInRow or less (when the end of the list is reached)

          # One function for taking a list with length nInRow or less and check for a specified color
          # The starting score is 0 in a row
          # We skip evaluation if the starting block is empty
          # As soon as the opposite color is found, return the score
          # When the right piece is found, keep track of how many spaces are checked
          # If another piece with the correct color is found, update the score by how many spaces were checked
          # Continue this check until the opposite color is found or the list ends
          
          # All 3 in a row will also count as a 2 in a row as a sublist, this is fine
          # Same logic for 4 in a row but bigger, which is also fine
          # All the scores for the AI-color are kept as is
          # All the scores gathered by opposite color are multiplied by -1
          # Then add all the score and that's our evaluation

          # List of evaluation criteria:
          # Piece in middle - 4 points
          # 2 in a row - 2 points
          # 3 in a row - 3 points
          # 4 in a row - 10000 points

          ai_score = 0
          other_score = 0
          for row in range(game.rows):
               for column in range(game.columns):
                    if game.board[row][column] is None:
                         continue # We skip if the starting spot is empty

                    directions_lists = self.get_all_directions_positions(row, column, game)
                    for direction in directions_lists:
                         ai_score += self.evaluate_list(deepcopy(direction), self, game)
                         other_score += self.evaluate_list(deepcopy(direction), game.otherPlayer, game)
          
          # Now for the discs in the middle
          # If the rows are uneven, just count the discs that are in row = game.rows//2
          # Else, count the two middle pillars, like game.rows//2 and game.rows//2 + 1
          middle_list = []
          if game.rows % 2 == 0:
               middle_list.append(self.get_row((game.rows//2, 0), game))
               middle_list.append(self.get_row((game.rows//2 + 1, 0), game))
          else:
               middle_list.append(self.get_row((game.rows//2, 0), game))
          for middle in middle_list:
               middle_names = [middle[i].name if not middle[i] is None else None for i in range(len(middle))]
               ai_score += middle_names.count(self.name) * 4
               other_score += middle_names.count(game.otherPlayer.name) * 4
          
          return (ai_score - other_score)
     
     def get_all_directions_positions(self, row, column, game):
          lists = []
          lists.append(self.get_row((row, column), game))
          lists.append(self.get_column((row, column), game))
          lists.append(self.get_diagonal((row, column), "left", game))
          lists.append(self.get_diagonal((row, column), "right", game))
          return lists

     def get_diagonal(self, position, direction, game):
          base_row = position[0]
          base_column = position[1]
          diagonal_list = []
          change = 1 if direction == "left" else -1

          while True:
               diagonal_list.append(game.board[base_row][base_column])
               base_column += 1
               base_row += change
               if base_row < 0 or base_row > game.rows-1 or base_column > game.columns-1:
                    break
          
          return diagonal_list


     def get_column(self, position, game):
          column_list = [game.board[position[0] + (i - position[0])][position[1]] for i in range(position[0], game.rows)]
          return column_list

     def get_row(self, position, game):
          row_list = [game.board[position[0]][position[1] + (i - position[1])] for i in range(position[1], game.columns)]
          return row_list

     def evaluate_list(self, positions, player, game):
          score = 0
          if len(positions) < 2:
               return score

          # We are going to take the first nInRow spots and evaluate those
          # When we are done evaluating, pop the first item and repeate
          # When the gets to less than / equal to nInRow, we don't evaluate if the starting spot is the opposite player
          while len(positions) > game.nInRow:
               active_positions = positions[:game.nInRow]
               disc_count = 0
               for position in active_positions:
                    if position is None:
                         continue
                    elif position.name == player.name:
                         disc_count += 1
                    else: # This is the opponents piece
                         if disc_count <= 1:
                              disc_count = 0
                         return score + disc_count # We stop everything and simply return the score for this list
               # If we are here, there were no opponent discs. Count the discs and pop the list
               positions.pop(0)
               if disc_count == game.nInRow:
                    score += 100000 # Victory
               elif disc_count > 1:
                    score += disc_count

          for square in positions:
               if not square is None:
                    if square.name != player.name: # This means this subset contains an opponent disc
                         return score

          while len(positions) > 1: # The length of the list is equal to 4 now
               positions_names = [positions[i].name if not positions[i] is None else None for i in range(len(positions))]
               if positions_names.count(player.name) > 1:
                    if positions_names.count(player.name) == game.nInRow:
                         score += 100000
                    score += positions_names.count(player.name)
               positions.pop(0)
          return score

     def draw_moves(self, game, board=None):
          pass
          game.draw()
          # test = True
          # while test:
          #      pygame.time.delay(1000)
          #      for event in pygame.event.get():
          #           if event.type == pygame.QUIT:
          #                pygame.quit()
          #           if event.type == pygame.KEYDOWN:
          #                if event.key == pygame.K_p:
          #                     test = False

class Random_player(Ai_player):
     def __init__(self, color, name):
          self.color = color
          self.name = name
          self.greyColor = list(map(lambda z: z//4 + 120, self.color)) # Change this for a nicer color
     
     def turn(self, game):
          available_rows = self.get_all_rows(game.board, self, game)
          row = random.choice(available_rows)
          column = game.getTopPos(row)
          return row, column

          

if __name__ == "__main__":
     Game = Board(7, 6, Ai_player((255, 0, 0), "Red Ai", 4), Ai_player((255, 255, 0), "Yellow Ai", 4), squareSize=120, squarePercentage=95, nInRow=4)
     Game.play()