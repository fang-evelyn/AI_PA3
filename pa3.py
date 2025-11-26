import copy
import random

class Node:
    def __init__(self, board, player_to_move, parent=None, move=None):
        self.board = board # The board's current state at this node
        self.player_to_move = player_to_move  # Whose turn is it at this node
        self.parent = parent
        self.move = move # Move that was taked to get here from parent
        self.children = {} # move -> child Node
        self.wi = 0.0 # total reward value of the node
        self.ni = 0 # visit count

class Board:
    
    def __init__(self, cols=7, rows=6):
        self.cols = cols
        self.rows = rows
        # None = empty, 1 = Red player, 2 = Yellow player
        self.board = [[None for _ in range(rows)] for _ in range(cols)]
    
    def clear_board(self, cols=7, rows=6):
        self.board = [[None for _ in range(rows)] for _ in range(cols)]

    def drop_in_slot(self, col, player):
        #drop a piece in column (1-7), modifies board in place
        col_index = col - 1
        #find first empty spot from bottom
        for i in range(self.rows):
            if self.board[col_index][i] is None:
                self.board[col_index][i] = player
                return
    
    def undo_move(self, col):
        #remove top piece from column 
        col_index = col - 1
        #find topmost piece and remove it
        for i in range(self.rows - 1, -1, -1):
            if self.board[col_index][i] is not None:
                self.board[col_index][i] = None
                return
    
    def is_slot_open(self, col):
        #check if column has space (1-7)
        col_index = col - 1
        if col_index < 0 or col_index >= self.cols:
            return False
        #check if top cell is empty
        return self.board[col_index][self.rows - 1] is None
    
    def get_legal_moves(self):
        #get all columns that aren't full (returns 1-7)
        return [col + 1 for col in range(self.cols) if self.is_slot_open(col + 1)]
    
    def is_full(self):
        #check if entire board is full
        for col in range(self.cols):
            if self.board[col][self.rows - 1] is None:
                return False
        return True
    
    def is_won_by(self, player):
        #check if player won any direction
        return (self._check_horizontal(player) or 
                self._check_vertical(player) or 
                self._check_diagonal_up(player) or 
                self._check_diagonal_down(player))
    
    def _has_win(self, player, cells):
        #check for 4 in a row in a list of cells
        count = 0
        for cell in cells:
            if cell == player:
                count += 1
                if count == 4:
                    return True
            else:
                count = 0
        return False
    
    def _check_horizontal(self, player):
        #check horizontal wins left/right
        for row in range(self.rows):
            row_cells = [self.board[col][row] for col in range(self.cols)]
            if self._has_win(player, row_cells):
                return True
        return False
    
    def _check_vertical(self, player):
        #check vertical wins up/down
        for col in range(self.cols):
            if self._has_win(player, self.board[col]):
                return True
        return False
    
    def _check_diagonal_up(self, player):
        #check diagonal wins bottom/left to top/right
        for start_col in range(self.cols - 3):
            for start_row in range(self.rows - 3):
                diag = [self.board[start_col + i][start_row + i] for i in range(4)]
                if all(cell == player for cell in diag):
                    return True
        return False
    
    def _check_diagonal_down(self, player):
        #check diagonal wins top/left to bottom/right
        for start_col in range(self.cols - 3):
            for start_row in range(3, self.rows):
                diag = [self.board[start_col + i][start_row - i] for i in range(4)]
                if all(cell == player for cell in diag):
                    return True
        return False
    
    def is_terminal(self):
        #check if game is over
        return self.is_won_by(1) or self.is_won_by(2) or self.is_full()
    
    def get_winner(self):
        #return winner: -1 (Red), 1 (Yellow), 0 (draw), None (not over)
        if self.is_won_by(1):
            return -1  # Red wins
        elif self.is_won_by(2):
            return 1   # Yellow wins
        elif self.is_full():
            return 0   # Draw
        else:
            return None  # Not over yet
    
    def board_to_str(self):
        #convert board to string (O=empty, R=Red, Y=Yellow)
        lines = []
        for row in range(self.rows - 1, -1, -1):
            row_chars = []
            for col in range(self.cols):
                cell = self.board[col][row]
                if cell is None:
                    row_chars.append('O')
                elif cell == 1:
                    row_chars.append('\033[91mR\033[0m') # Text between "\033[91m" and "\033[0m" is actual text turned red
                else:  #cell == 2
                    row_chars.append('\033[33mY\033[0m') # Text between "\033[33m" and "\033[0m" is actual text turned yellow3
            lines.append(''.join(row_chars))
        return '\n'.join(lines)
    
    def __str__(self):
        return self.board_to_str()

    def play_manual(self):
        self.clear_board() # making sure we play with a clean board

        turn = 0 # tracks turns
        while not self.is_terminal(): # while the game is not over, keep looping
            print(f"Current Board:\n{board}")
            if turn % 2 == 0: # for red player's turn
                print("\nRed Player Turn: ")
                legal = self.get_legal_moves() # obtain and list the possible moves for the player
                print(f"All Legal moves: {legal}")
            
                # Checking to make sure the move the player entered is valid
                valid_move = False
                while not valid_move:
                    col_drop = int(input("\nPlease choose a valid column to drop in: "))
                    if col_drop in legal: # if legal move, accept it and break out of loop
                        valid_move = True
            
                self.drop_in_slot(col_drop, 1) # making player move
            else: # Yello player's turn
                print("\nYellow Player Turn: ")
                legal = self.get_legal_moves() # Obtain and list the possible moves for the player
                print(f"All Legal moves: {legal}")
            
                # Checking to make sure the move the player entered is valid
                valid_move = False
                while not valid_move:
                    col_drop = int(input("\nPlease choose a valid column to drop in: "))
                    if col_drop in legal: # if legal move, accept and break out of loop
                        valid_move = True
            
                self.drop_in_slot(col_drop, 2) # making player move
        
            turn += 1 # incrementing the turn count to track which player is next

        print(f"Final Board of Manual Playing:\n\n{board}\n")

        winner = self.get_winner() # finding out who won
        if winner == -1: # Red Player Win
            print(f"Red Player Wins In {turn} turns!")
        elif winner == 1: # Yellow Player Win
            print(f"Yellow Player Wins In {turn} turns!")
        else: # Game ended in a Draw
            print("Game was a DRAW!")

    def play_UR(self):
        self.clear_board() # Making sure we play with a clean board

        turn = 0 # Tracking turns
        while not self.is_terminal():
            if turn % 2 == 0: # Player's turn
                print(f"Current Board During UR:\n{board}") # displays updated board to player

                print("\nRed Player Turn: ")
                legal = self.get_legal_moves() # obtain and list the possible moves for the player
                print(f"All Legal moves: {legal}")
            
                # Checking to make sure the move the player entered is valid
                valid_move = False
                while not valid_move:
                    col_drop = int(input("\nPlease choose a valid column to drop in: "))
                    if col_drop in legal: # if legal move, accept it and break out of loop
                        valid_move = True
            
                self.drop_in_slot(col_drop, 1) # making player move
            else: # Uniform Random turn
                legal = self.get_legal_moves() # obtaining a list of possible moves

                chosen_move = random.choice(legal)

                print(f"\nFINAL Move Selected: {chosen_move}\n")

                self.drop_in_slot(chosen_move, 2) # playing the randomly chosen move
            turn += 1 # incrementing turn value

        print(f"Final Board of Uniform Random Playing:\n\n{board}\n")

        winner = self.get_winner() # finding out who won
        if winner == -1: # Player Wins
            print(f"Red Player (Person) Wins In {turn} turns!")
        elif winner == 1: # Uniform Random Wins
            print(f"Yellow Player (UR) Wins In {turn} turns!")
        else: # Game ended in a Draw
            print("Game was a DRAW!")

    def pmcgs_best_move(self, player, num_simulations = 500, verbose = False):

        # Root node = a copy of the current board, player = 1 (red) or 2 (yellow)
        root_board = copy.deepcopy(self)
        root = Node(root_board, player_to_move = player)

        for _ in range(num_simulations):
            node = root
            path = [node]

            while True:
                # If full, or game won, stop the selection and/or expansion
                if node.board.is_terminal():
                    break

                legal_moves = node.board.get_legal_moves()

                if not legal_moves: # if no leagal moves, break
                    break

                # Inside of the tree: choose a move at random
                if verbose: # printing info if verbose option is chosen
                    print(f"wi: {(node.wi)}")
                    print(f"ni: {node.ni}")

                chosen_move = random.choice(legal_moves) # choosing move for this simulation at random

                if verbose: # printing info if verbose option is chosen
                    print(f"Move selected: {chosen_move}")

                if chosen_move in node.children:
                    # Move is already in tree: go to that child
                    node = node.children[chosen_move]
                    path.append(node)
                else:
                    # if move is not in tree
                    # Creating the new board with the move
                    new_board = copy.deepcopy(node.board)
                    new_board.drop_in_slot(chosen_move, node.player_to_move)

                    # updating the tree
                    next_player = 1 if node.player_to_move == 2 else 2
                    child = Node(new_board, player_to_move=next_player, parent=node, move = chosen_move)
                    node.children[chosen_move] = child
                    node = child
                    path.append(node)

                    if verbose: # print statement for verbose mode
                        print("NODE ADDED")
                    break  # we shouldonly add one new node per simulation

            # set up the rollout
            rollout_board = copy.deepcopy(node.board)
            current_player = node.player_to_move

            while not rollout_board.is_terminal(): # while the game is not over (full or won)
                legal_moves = rollout_board.get_legal_moves() # obtaining legal moves
                move = random.choice(legal_moves) # choosing move at random
                if verbose: # verbose print statement
                    print(f"Move selected: {move}")

                # changing the current player after making play
                rollout_board.drop_in_slot(move, current_player)
                current_player = 1 if current_player == 2 else 2

            # Terminal node: get value from root player's perspective
            winner = rollout_board.get_winner()  # -1 for red, 0 for draw, or 1 for yellow
            value = self.get_result_helper(winner, player)

            if verbose: # verbose print statement
                print(f"TERMINAL NODE VALUE: {value}")

            # Tracing the path to update visits and rewards
            for n in path:
                n.ni += 1
                n.wi += value

                if verbose: # verbose print statement
                    print("Updated values:")
                    print(f"wi: {(n.wi)}")
                    print(f"ni: {n.ni}")

        # After running simulations, only consider the legal moves at root
        legal_root_moves = root.board.get_legal_moves()

        move_values = {} # dictionary for storing the values of moves for each column
        for col in range(1, self.cols + 1): # traversing all columns
            if col not in legal_root_moves:  # if we can't play in column, there is no value, and should be null
                print(f"Column {col}: Null")
                move_values[col] = None
            else: # if the move is legal
                child = root.children.get(col)
                if child is None or child.ni == 0:
                    # this is a Legal move, but was never visited, value is 0
                    val = 0.0
                else: # column was legal and visited
                    val = child.wi / child.ni # average reward for move
                move_values[col] = val
                print(f"Column {col}: {val:.2f}")

        # Choosing the move with the highest value
        best_move = None
        best_val = float('-inf') # negative infinity as the lowest value, to be updated with higher values
        for col, val in move_values.items():
            if val is None: # if column value is null
                continue
            if val > best_val: # updating value and tracking column
                best_val = val
                best_move = col

        print(f"FINAL Move selected: {best_move}")
        return best_move

    def get_result_helper(self, winner, player):
            if winner == 0: # if no winner, game was a draw
                return 0
            if winner == -1:  # Red wins
                return 1 if player == 1 else -1
            if winner == 1:   # Yellow wins
                return 1 if player == 2 else -1
            return 0  # shouldn't happen

    def play_PMCGS(self, simulations_per_move=500, verbose=False): 
        self.clear_board() # clean board
        turn = 0 # tracking turns played

        while not self.is_terminal(): # while board is not full and game is not over
            print(f"Current Board During PMCGS:\n{board}")

            if turn % 2 == 0: # Red Turn, player
                print("\nRed Player Turn: ")
                legal = self.get_legal_moves() # obtaining legal moves and displaying them to player
                print(f"All Legal moves: {legal}")

                # choosing a move and making sure it is valud
                valid_move = False
                while not valid_move:
                    col_drop = int(input("\nPlease choose a valid column to drop in: "))
                    if col_drop in legal:
                        valid_move = True

                self.drop_in_slot(col_drop, 1) # playing valid move
            else:
                # PMCGS algorithm (Yellow)
                print("\nYellow Player Turn (PMCGS): ")

                #Determining best move using PMCGS algorithm
                best_move = self.pmcgs_best_move(player=2, num_simulations=simulations_per_move, verbose=verbose)
                self.drop_in_slot(best_move, 2) # playing best move

            turn += 1 # incrementing turn order

        print(f"Final Board of PMCGS Playing:\n\n{board}\n")

        winner = self.get_winner() # finding out who won if any

        if winner == -1:
            print(f"Red Player (Human) Wins In {turn} turns!")
        elif winner == 1:
            print(f"Yellow Player (PMCGS) Wins In {turn} turns!")
        else:
            print("Game was a DRAW!")



if __name__ == "__main__":
    board = Board() # create an empty board for a new game
    
    # board.play_manual()
    # print(f"Board after manual play:\n{board}")
    # board.play_UR()
    # print(f"Board after UR play:\n{board}")
    board.play_PMCGS(verbose = False)
  