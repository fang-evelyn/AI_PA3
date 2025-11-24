class Board:
    
    def __init__(self, cols=7, rows=6):
        self.cols = cols
        self.rows = rows
        # None = empty, 1 = Red player, 2 = Yellow player
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
                    row_chars.append('R')
                else:  #cell == 2
                    row_chars.append('Y')
            lines.append(''.join(row_chars))
        return '\n'.join(lines)
    
    def __str__(self):
        return self.board_to_str()


def read_board_from_file(filename): #for the files we need to test here
    #returns algorithm, player, board
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f.readlines()]
    
    algorithm = lines[0]  #UR, PMCGS, or UCT
    player_char = lines[1]  #R or Y
    player = 1 if player_char == 'R' else 2
    
    #read 6 rows of board (lines 3-8)
    board = Board()
    board_lines = lines[2:8]
    
    #process each row 
    for row_idx, line in enumerate(board_lines):
        actual_row = 5 - row_idx  #convert to board coordinates
        for col_idx, char in enumerate(line):
            if char == 'R':
                board.board[col_idx][actual_row] = 1
            elif char == 'Y':
                board.board[col_idx][actual_row] = 2
            #0 stays None, empty
    
    return algorithm, player, board

if __name__ == "__main__":
    board = Board() 