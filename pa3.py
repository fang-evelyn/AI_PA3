import random
import math
import sys

# Board implementation - optimized version
class Board:
    def __init__(self, cols=7, rows=6):
        self.cols = cols
        self.rows = rows
        self.board = [[None for _ in range(rows)] for _ in range(cols)]
        self.heights = [0] * cols  # Track height of each column for faster operations
        self.last_move = None  # Track last move for faster win checking
    
    def drop_in_slot(self, col, player):
        col_index = col - 1
        row = self.heights[col_index]
        self.board[col_index][row] = player
        self.heights[col_index] += 1
        self.last_move = (col_index, row, player)
        return (col_index, row)
    
    def undo_move(self, col):
        col_index = col - 1
        self.heights[col_index] -= 1
        self.board[col_index][self.heights[col_index]] = None
        self.last_move = None
    
    def is_slot_open(self, col):
        col_index = col - 1
        if col_index < 0 or col_index >= self.cols:
            return False
        return self.heights[col_index] < self.rows
    
    def get_legal_moves(self):
        return [col + 1 for col in range(self.cols) if self.heights[col] < self.rows]
    
    def is_full(self):
        return all(h == self.rows for h in self.heights)
    
    def check_win_from_last_move(self):
        """Only check win condition around the last move - much faster"""
        if self.last_move is None:
            return None
        
        col, row, player = self.last_move
        
        # Check horizontal
        count = 1
        # Check left
        c = col - 1
        while c >= 0 and self.board[c][row] == player:
            count += 1
            c -= 1
        # Check right
        c = col + 1
        while c < self.cols and self.board[c][row] == player:
            count += 1
            c += 1
        if count >= 4:
            return player
        
        # Check vertical (only need to check down)
        count = 1
        r = row - 1
        while r >= 0 and self.board[col][r] == player:
            count += 1
            r -= 1
        if count >= 4:
            return player
        
        # Check diagonal (bottom-left to top-right)
        count = 1
        c, r = col - 1, row - 1
        while c >= 0 and r >= 0 and self.board[c][r] == player:
            count += 1
            c -= 1
            r -= 1
        c, r = col + 1, row + 1
        while c < self.cols and r < self.rows and self.board[c][r] == player:
            count += 1
            c += 1
            r += 1
        if count >= 4:
            return player
        
        # Check diagonal (top-left to bottom-right)
        count = 1
        c, r = col - 1, row + 1
        while c >= 0 and r < self.rows and self.board[c][r] == player:
            count += 1
            c -= 1
            r += 1
        c, r = col + 1, row - 1
        while c < self.cols and r >= 0 and self.board[c][r] == player:
            count += 1
            c += 1
            r -= 1
        if count >= 4:
            return player
        
        return None
    
    def is_terminal_fast(self):
        """Fast terminal check using last move"""
        if self.last_move is not None:
            winner = self.check_win_from_last_move()
            if winner is not None:
                return True
        return self.is_full()
    
    def get_winner_fast(self):
        """Get winner based on last move"""
        if self.last_move is not None:
            winner = self.check_win_from_last_move()
            if winner == 1:
                return -1
            elif winner == 2:
                return 1
        if self.is_full():
            return 0
        return None
    
    # Keep old methods for file reading
    def is_won_by(self, player):
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
            if self._has_win(player, self.board[col][:self.heights[col]]):
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
        self.wi = 0
        self.ni = 0


def uniform_random(board):
    legal_moves = board.get_legal_moves()
    selected_move = random.choice(legal_moves)
    print(f"FINAL Move selected: {selected_move}")
    return selected_move


def calculate_ucb(parent_visits, child_wins, child_visits, is_maximizing_player):
    if child_visits == 0:
        return float('inf') if is_maximizing_player else float('-inf')
    
    exploitation_value = child_wins / child_visits
    exploration_bonus = 1.41 * math.sqrt(math.log(parent_visits) / child_visits)
    
    if is_maximizing_player:
        return exploitation_value + exploration_bonus
    else:
        return exploitation_value - exploration_bonus


def run_mcts(board, player, num_simulations, use_uct, verbose_mode):
    root = Node()
    
    for simulation in range(num_simulations):
        current_node = root
        current_player = player
        path = [current_node]
        moves_made = []
        
        # Selection and Expansion phase
        while not board.is_terminal_fast():
            legal_moves = board.get_legal_moves()
            untried_moves = [m for m in legal_moves if m not in current_node.children]
            
            if untried_moves:
                selected_move = random.choice(untried_moves)
                
                if verbose_mode:
                    print(f"wi: {current_node.wi}")
                    print(f"ni: {current_node.ni}")
                    if use_uct and current_node.children:
                        for col in range(1, 8):
                            if col in current_node.children:
                                child = current_node.children[col]
                                ucb_val = calculate_ucb(current_node.ni, child.wi, child.ni, current_player == 2)
                                print(f"V{col}: {'inf' if ucb_val == float('inf') or ucb_val == float('-inf') else f'{ucb_val:.2f}'}")
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
                if use_uct:
                    if verbose_mode:
                        print(f"wi: {current_node.wi}")
                        print(f"ni: {current_node.ni}")
                        for col in range(1, 8):
                            if col in current_node.children:
                                child = current_node.children[col]
                                ucb_val = calculate_ucb(current_node.ni, child.wi, child.ni, current_player == 2)
                                print(f"V{col}: {'inf' if ucb_val == float('inf') or ucb_val == float('-inf') else f'{ucb_val:.2f}'}")
                    
                    best_move = None
                    best_ucb = float('-inf') if current_player == 2 else float('inf')
                    
                    for move, child in current_node.children.items():
                        ucb_value = calculate_ucb(current_node.ni, child.wi, child.ni, current_player == 2)
                        if (current_player == 2 and ucb_value > best_ucb) or \
                           (current_player == 1 and ucb_value < best_ucb):
                            best_ucb = ucb_value
                            best_move = move
                    
                    selected_move = best_move
                else:
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
        
        # Simulation phase
        while not board.is_terminal_fast():
            random_move = random.choice(board.get_legal_moves())
            if verbose_mode:
                print(f"Move selected: {random_move}")
            board.drop_in_slot(random_move, current_player)
            moves_made.append(random_move)
            current_player = 3 - current_player
        
        final_value = board.get_winner_fast()
        if verbose_mode:
            print(f"TERMINAL NODE VALUE: {final_value}")
        
        # Backpropagation
        for node in reversed(path):
            node.ni += 1
            node.wi += final_value
            if verbose_mode:
                print("Updated values:")
                print(f"wi: {node.wi}")
                print(f"ni: {node.ni}")
        
        # Undo all moves
        for _ in moves_made:
            board.undo_move(moves_made.pop())
    
    # Print final column values
    for col in range(1, 8):
        if col in root.children:
            child = root.children[col]
            avg_value = child.wi / child.ni
            print(f"Column {col}: {avg_value:.2f}")
        else:
            print(f"Column {col}: Null")
    
    # Select best move
    best_move = None
    best_avg = float('-inf') if player == 2 else float('inf')
    
    for move, child in root.children.items():
        if child.ni > 0:
            avg = child.wi / child.ni
            if (player == 2 and avg > best_avg) or (player == 1 and avg < best_avg):
                best_avg = avg
                best_move = move
    
    print(f"FINAL Move selected: {best_move}")
    return best_move


def read_board_from_file(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f.readlines()]
    
    algorithm = lines[0]
    player_char = lines[1]
    player = 1 if player_char == 'R' else 2
    
    board = Board()
    board_lines = lines[2:8]
    
    for row_idx in range(len(board_lines)):
        line = board_lines[row_idx]
        actual_row = 5 - row_idx
        for col_idx in range(len(line)):
            char = line[col_idx]
            if char in ('R', 'Y'):
                p = 1 if char == 'R' else 2
                board.board[col_idx][actual_row] = p
                board.heights[col_idx] = max(board.heights[col_idx], actual_row + 1)
    
    return algorithm, player, board


def play_full_game(algo1, params1, algo2, params2):
    board = Board()
    current_player = 1
    player_algos = {1: (algo1, params1), 2: (algo2, params2)}
    
    move_count = 0
    while not board.is_terminal_fast() and move_count < 42:
        algo_name, algo_params = player_algos[current_player]
        
        if algo_name == "UR":
            move = random.choice(board.get_legal_moves())
        else:
            root = Node()
            use_uct = (algo_name == "UCT")
            
            for _ in range(algo_params):
                node = root
                player = current_player
                path = [node]
                moves_made = []
                
                while not board.is_terminal_fast():
                    moves = board.get_legal_moves()
                    untried = [m for m in moves if m not in node.children]
                    
                    if untried:
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
                            best_m = None
                            best_ucb = float('-inf') if player == 2 else float('inf')
                            for m, ch in node.children.items():
                                ucb = calculate_ucb(node.ni, ch.wi, ch.ni, player == 2)
                                if (player == 2 and ucb > best_ucb) or (player == 1 and ucb < best_ucb):
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
                
                # Rollout
                while not board.is_terminal_fast():
                    m = random.choice(board.get_legal_moves())
                    board.drop_in_slot(m, player)
                    moves_made.append(m)
                    player = 3 - player
                
                value = board.get_winner_fast()
                
                # Backprop
                for n in reversed(path):
                    n.ni += 1
                    n.wi += value
                
                # Undo
                for _ in range(len(moves_made)):
                    board.undo_move(moves_made.pop())
            
            # Pick best move
            best_move = None
            best_val = float('-inf') if current_player == 2 else float('inf')
            for m, ch in root.children.items():
                if ch.ni > 0:
                    val = ch.wi / ch.ni
                    if (current_player == 2 and val > best_val) or (current_player == 1 and val < best_val):
                        best_val = val
                        best_move = m
            move = best_move
        
        board.drop_in_slot(move, current_player)
        current_player = 3 - current_player
        move_count += 1
    
    winner = board.get_winner_fast()
    return 1 if winner == -1 else (2 if winner == 1 else 0)


def run_tournament():
    algorithms = [
        ("UR", 0),
        ("PMCGS", 500),
        ("PMCGS", 10000),
        ("UCT", 500),
        ("UCT", 10000)
    ]
    
    names = ["UR", "PMCGS(500)", "PMCGS(10000)", "UCT(500)", "UCT(10000)"]
    results = [[0 for _ in range(5)] for _ in range(5)]
    
    print("Starting tournament...")
    print("This will take a while...\n")
    
    for i in range(5):
        for j in range(5):
            print(f"Testing {names[i]} vs {names[j]}... ", end="", flush=True)
            
            wins = 0
            draws = 0
            for _ in range(100):
                winner = play_full_game(algorithms[i][0], algorithms[i][1],
                                       algorithms[j][0], algorithms[j][1])
                if winner == 1:
                    wins += 1
                elif winner == 0:
                    draws += 1
            
            results[i][j] = wins
            print(f"{wins} wins, {draws} draws")
    
    print("\n" + "="*80)
    print("TOURNAMENT RESULTS")
    print("="*80)
    print(f"{'':15}", end="")
    for name in names:
        print(f"{name:15}", end="")
    print("\n" + "-"*80)
    
    for i in range(5):
        print(f"{names[i]:15}", end="")
        for j in range(5):
            print(f"{results[i][j]:15}", end="")
        print()
    print()


if __name__ == "__main__":
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