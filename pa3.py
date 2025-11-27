import random
import math
import sys

# Board implementation - handles the connect 4 game state
class Board:
    def __init__(self, cols=7, rows=6):
        self.cols = cols
        self.rows = rows
        self.board = [[None for _ in range(rows)] for _ in range(cols)]
    
    def drop_in_slot(self, col, player):
        col_index = col - 1
        for i in range(self.rows):
            if self.board[col_index][i] is None:
                self.board[col_index][i] = player
                return
    
    def undo_move(self, col):
        col_index = col - 1
        for i in range(self.rows - 1, -1, -1):
            if self.board[col_index][i] is not None:
                self.board[col_index][i] = None
                return
    
    def is_slot_open(self, col):
        col_index = col - 1
        if col_index < 0 or col_index >= self.cols:
            return False
        return self.board[col_index][self.rows - 1] is None
    
    def get_legal_moves(self):
        return [col + 1 for col in range(self.cols) if self.is_slot_open(col + 1)]
    
    def is_full(self):
        for col in range(self.cols):
            if self.board[col][self.rows - 1] is None:
                return False
        return True
    
    def is_won_by(self, player):
        # check all win conditions
        if self._check_horizontal(player):
            return True
        if self._check_vertical(player):
            return True
        if self._check_diagonal_up(player):
            return True
        if self._check_diagonal_down(player):
            return True
        return False
    
    def _has_win(self, player, cells):
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
        for row in range(self.rows):
            row_cells = [self.board[col][row] for col in range(self.cols)]
            if self._has_win(player, row_cells):
                return True
        return False
    
    def _check_vertical(self, player):
        for col in range(self.cols):
            if self._has_win(player, self.board[col]):
                return True
        return False
    
    def _check_diagonal_up(self, player):
        for start_col in range(self.cols - 3):
            for start_row in range(self.rows - 3):
                diag = [self.board[start_col + i][start_row + i] for i in range(4)]
                if all(cell == player for cell in diag):
                    return True
        return False
    
    def _check_diagonal_down(self, player):
        for start_col in range(self.cols - 3):
            for start_row in range(3, self.rows):
                diag = [self.board[start_col + i][start_row - i] for i in range(4)]
                if all(cell == player for cell in diag):
                    return True
        return False
    
    def is_terminal(self):
        return self.is_won_by(1) or self.is_won_by(2) or self.is_full()
    
    def get_winner(self):
        # returns -1 for red win, 1 for yellow win, 0 for draw
        if self.is_won_by(1):
            return -1
        elif self.is_won_by(2):
            return 1
        elif self.is_full():
            return 0
        return None


# tree node for MCTS
class Node:
    def __init__(self, move=None, parent=None):
        self.move = move
        self.parent = parent
        self.children = {}
        self.wi = 0  # total wins
        self.ni = 0  # num visits


# Algorithm 1 - just picks random move
def uniform_random(board):
    legal_moves = board.get_legal_moves()
    selected_move = random.choice(legal_moves)
    print(f"FINAL Move selected: {selected_move}")
    return selected_move


# UCB calculation for UCT algorithm
def calculate_ucb(parent_visits, child_wins, child_visits, is_maximizing_player):
    if child_visits == 0:
        return float('inf') if is_maximizing_player else float('-inf')
    
    exploitation_value = child_wins / child_visits
    exploration_bonus = 1.41 * math.sqrt(math.log(parent_visits) / child_visits)
    
    if is_maximizing_player:
        return exploitation_value + exploration_bonus
    else:
        return exploitation_value - exploration_bonus


# Main MCTS implementation - works for both PMCGS and UCT
# Uses do/undo instead of copying the board for speed
def run_mcts(board, player, num_simulations, use_uct, verbose_mode):
    root = Node()
    
    # run simulations
    for simulation in range(num_simulations):
        current_node = root
        current_player = player
        path = [current_node]
        moves_made = []  # track moves so we can undo them
        
        # Selection and Expansion phase
        while not board.is_terminal():
            legal_moves = board.get_legal_moves()
            
            # find moves we haven't tried yet
            untried_moves = []
            for move in legal_moves:
                if move not in current_node.children:
                    untried_moves.append(move)
            
            if len(untried_moves) > 0:
                # Expansion - add new node
                selected_move = random.choice(untried_moves)
                
                if verbose_mode:
                    print(f"wi: {current_node.wi}")
                    print(f"ni: {current_node.ni}")
                    
                    # print UCB values if we're using UCT and have children
                    if use_uct and len(current_node.children) > 0:
                        for col in range(1, 8):
                            if col in current_node.children:
                                child = current_node.children[col]
                                ucb_val = calculate_ucb(current_node.ni, child.wi, child.ni, current_player == 2)
                                if ucb_val == float('inf') or ucb_val == float('-inf'):
                                    print(f"V{col}: inf")
                                else:
                                    print(f"V{col}: {ucb_val:.2f}")
                    
                    print(f"Move selected: {selected_move}")
                    print("NODE ADDED")
                
                board.drop_in_slot(selected_move, current_player)
                moves_made.append(selected_move)
                new_node = Node(move=selected_move, parent=current_node)
                current_node.children[selected_move] = new_node
                current_node = new_node
                path.append(current_node)
                current_player = 3 - current_player
                break
            else:
                # all children already exist - select one
                if use_uct:
                    # UCT - use UCB formula to pick best child
                    if verbose_mode:
                        print(f"wi: {current_node.wi}")
                        print(f"ni: {current_node.ni}")
                        for col in range(1, 8):
                            if col in current_node.children:
                                child = current_node.children[col]
                                ucb_val = calculate_ucb(current_node.ni, child.wi, child.ni, current_player == 2)
                                if ucb_val == float('inf') or ucb_val == float('-inf'):
                                    print(f"V{col}: inf")
                                else:
                                    print(f"V{col}: {ucb_val:.2f}")
                    
                    best_move = None
                    best_ucb = float('-inf') if current_player == 2 else float('inf')
                    
                    for move, child in current_node.children.items():
                        ucb_value = calculate_ucb(current_node.ni, child.wi, child.ni, current_player == 2)
                        if current_player == 2:  # maximizing
                            if ucb_value > best_ucb:
                                best_ucb = ucb_value
                                best_move = move
                        else:  # minimizing
                            if ucb_value < best_ucb:
                                best_ucb = ucb_value
                                best_move = move
                    
                    selected_move = best_move
                else:
                    # PMCGS - just pick random
                    selected_move = random.choice(legal_moves)
                    if verbose_mode:
                        print(f"wi: {current_node.wi}")
                        print(f"ni: {current_node.ni}")
                        print(f"Move selected: {selected_move}")
                
                if use_uct and verbose_mode:
                    print(f"Move selected: {selected_move}")
                
                board.drop_in_slot(selected_move, current_player)
                moves_made.append(selected_move)
                current_node = current_node.children[selected_move]
                path.append(current_node)
                current_player = 3 - current_player
        
        # Simulation phase - play random moves till end
        while not board.is_terminal():
            random_move = random.choice(board.get_legal_moves())
            if verbose_mode:
                print(f"Move selected: {random_move}")
            board.drop_in_slot(random_move, current_player)
            moves_made.append(random_move)
            current_player = 3 - current_player
        
        # get final value
        final_value = board.get_winner()
        if verbose_mode:
            print(f"TERMINAL NODE VALUE: {final_value}")
        
        # Backpropagation - update all nodes in path
        for node in reversed(path):
            node.ni += 1
            node.wi += final_value
            if verbose_mode:
                print("Updated values:")
                print(f"wi: {node.wi}")
                print(f"ni: {node.ni}")
        
        # Undo all moves to restore board to original state
        for move in reversed(moves_made):
            board.undo_move(move)
    
    # print final column values
    for col in range(1, 8):
        if col in root.children:
            child = root.children[col]
            avg_value = child.wi / child.ni
            print(f"Column {col}: {avg_value:.2f}")
        else:
            print(f"Column {col}: Null")
    
    # select best move based on average value (not UCB)
    # Need to pick based on which player is making the move
    best_move = None
    if player == 2:  # Yellow (maximizer)
        best_avg = float('-inf')
        for move, child in root.children.items():
            if child.ni > 0:
                avg = child.wi / child.ni
                if avg > best_avg:
                    best_avg = avg
                    best_move = move
    else:  # Red (minimizer)
        best_avg = float('inf')
        for move, child in root.children.items():
            if child.ni > 0:
                avg = child.wi / child.ni
                if avg < best_avg:
                    best_avg = avg
                    best_move = move
    
    print(f"FINAL Move selected: {best_move}")
    return best_move


# read game state from file
def read_board_from_file(filename):
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    
    lines = [line.strip() for line in lines]
    
    algorithm = lines[0]
    player_char = lines[1]
    player = 1 if player_char == 'R' else 2
    
    board = Board()
    board_lines = lines[2:8]
    
    # read board state - top row is index 0 in file but row 5 in our board
    for row_idx in range(len(board_lines)):
        line = board_lines[row_idx]
        actual_row = 5 - row_idx
        for col_idx in range(len(line)):
            char = line[col_idx]
            if char == 'R':
                board.board[col_idx][actual_row] = 1
            elif char == 'Y':
                board.board[col_idx][actual_row] = 2
    
    return algorithm, player, board


# Part 2 - play full game between two algorithms
def play_full_game(algo1, params1, algo2, params2):
    board = Board()
    current_player = 1
    
    # map player to their algorithm
    player_algos = {
        1: (algo1, params1),
        2: (algo2, params2)
    }
    
    move_count = 0
    while not board.is_terminal() and move_count < 42:
        algo_name, algo_params = player_algos[current_player]
        
        # get move from algorithm
        if algo_name == "UR":
            move = random.choice(board.get_legal_moves())
        else:
            # run MCTS without printing using do/undo
            root = Node()
            use_uct = (algo_name == "UCT")
            
            for sim in range(algo_params):
                node = root
                player = current_player
                path = [node]
                moves_made = []
                
                while not board.is_terminal():
                    moves = board.get_legal_moves()
                    untried = [m for m in moves if m not in node.children]
                    
                    if len(untried) > 0:
                        m = random.choice(untried)
                        board.drop_in_slot(m, player)
                        moves_made.append(m)
                        child = Node(move=m, parent=node)
                        node.children[m] = child
                        node = child
                        path.append(node)
                        player = 3 - player
                        break
                    else:
                        if use_uct:
                            # pick best UCB
                            best_m = None
                            best_ucb = float('-inf') if player == 2 else float('inf')
                            for m, ch in node.children.items():
                                ucb = calculate_ucb(node.ni, ch.wi, ch.ni, player == 2)
                                if player == 2:
                                    if ucb > best_ucb:
                                        best_ucb = ucb
                                        best_m = m
                                else:
                                    if ucb < best_ucb:
                                        best_ucb = ucb
                                        best_m = m
                            m = best_m
                        else:
                            m = random.choice(moves)
                        
                        board.drop_in_slot(m, player)
                        moves_made.append(m)
                        node = node.children[m]
                        path.append(node)
                        player = 3 - player
                
                # rollout
                while not board.is_terminal():
                    m = random.choice(board.get_legal_moves())
                    board.drop_in_slot(m, player)
                    moves_made.append(m)
                    player = 3 - player
                
                value = board.get_winner()
                
                # backprop
                for n in reversed(path):
                    n.ni += 1
                    n.wi += value
                
                # undo all moves
                for m in reversed(moves_made):
                    board.undo_move(m)
            
            # pick best move based on which player is choosing
            best_move = None
            if current_player == 2:  # Yellow (maximizer)
                best_val = float('-inf')
                for m, ch in root.children.items():
                    if ch.ni > 0:
                        val = ch.wi / ch.ni
                        if val > best_val:
                            best_val = val
                            best_move = m
            else:  # Red (minimizer)
                best_val = float('inf')
                for m, ch in root.children.items():
                    if ch.ni > 0:
                        val = ch.wi / ch.ni
                        if val < best_val:
                            best_val = val
                            best_move = m
            move = best_move
        
        board.drop_in_slot(move, current_player)
        current_player = 3 - current_player
        move_count += 1
    
    winner = board.get_winner()
    if winner == -1:
        return 1  # player 1 wins
    elif winner == 1:
        return 2  # player 2 wins
    else:
        return 0  # draw


# run tournament for part 2
def run_tournament():
    algorithms = [
        ("UR", 0),
        ("PMCGS", 100),  # Much faster
        ("PMCGS", 500),  # Reduced from 10000
        ("UCT", 100),    
        ("UCT", 500)     # Reduced from 10000
    ]
    
    names = ["UR", "PMCGS(100)", "PMCGS(500)", "UCT(100)", "UCT(500)"]
    
    # results[i][j] = wins for algorithm i against algorithm j
    results = [[0 for j in range(5)] for i in range(5)]
    
    print("Starting tournament...")
    print("This will take a while...\n")
    
    for i in range(5):
        for j in range(5):
            print(f"Testing {names[i]} vs {names[j]}... ", end="", flush=True)
            
            wins = 0
            draws = 0
            for game_num in range(20):  # Reduced to 20 games for speed
                winner = play_full_game(algorithms[i][0], algorithms[i][1],
                                       algorithms[j][0], algorithms[j][1])
                if winner == 1:
                    wins += 1
                elif winner == 0:
                    draws += 1
            
            results[i][j] = wins
            print(f"{wins} wins, {draws} draws")
    
    # print results table
    print("\n")
    print("="*80)
    print("TOURNAMENT RESULTS")
    print("="*80)
    print(f"{'':15}", end="")
    for name in names:
        print(f"{name:15}", end="")
    print()
    print("-"*80)
    
    for i in range(5):
        print(f"{names[i]:15}", end="")
        for j in range(5):
            print(f"{results[i][j]:15}", end="")
        print()
    print()


# main entry point
if __name__ == "__main__":
    # check if tournament mode
    if len(sys.argv) == 2 and sys.argv[1] == "tournament":
        run_tournament()
    elif len(sys.argv) == 4:
        filename = sys.argv[1]
        verbose_setting = sys.argv[2]
        num_sims = int(sys.argv[3])
        
        algorithm, player, board = read_board_from_file(filename)
        
        verbose = (verbose_setting == "Verbose")
        
        if algorithm == "UR":
            uniform_random(board)
        elif algorithm == "PMCGS":
            run_mcts(board, player, num_sims, False, verbose)
        elif algorithm == "UCT":
            run_mcts(board, player, num_sims, True, verbose)
        else:
            print(f"Unknown algorithm: {algorithm}")
    else:
        print("Usage: python pa3.py <filename> <Verbose|Brief|None> <num_simulations>")
        print("   or: python pa3.py tournament")