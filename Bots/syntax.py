import numpy as np
import time
from Bots.ChessBotList import register_chess_bot

pieces_values = {'p':1, 'n':3, 'b':3, 'r':5, 'q':9, 'k':100}

INF = 10**9

class TimeUp(Exception):
    pass

def get_piece_value(piece_type):
    return pieces_values.get(piece_type, 0)

def evaluate_board(board):
    score = 0
    for x in range(board.shape[0]):
        for y in range(board.shape[1]):
            piece = board[x, y]
            if piece == '':
                continue
            value = get_piece_value(piece[0])
            if piece[-1] == 'w':
                score += value
            else:
                score -= value
    return score

def apply_move(board, move):
    (fx, fy), (tx, ty) = move
    new_board = np.empty_like(board)
    for i in range(board.shape[0]):
        for j in range(board.shape[1]):
            new_board[i, j] = board[i, j]
    
    piece = new_board[fx, fy]
    if piece[0] == 'p' and (tx == 0 or tx == board.shape[0] - 1):
        new_board[tx, ty] = 'q' + piece[-1]
    else:
        new_board[tx, ty] = piece
    new_board[fx, fy] = ''
    return new_board

def can_piece_reach(board, piece_pos, target_pos, piece_type, color):
    px, py = piece_pos
    tx, ty = target_pos
    
    if piece_type == 'p':
        if color == 'w':
            return tx == px + 1 and abs(ty - py) == 1
        else:
            return tx == px - 1 and abs(ty - py) == 1
    
    elif piece_type == 'n':
        return (abs(tx - px), abs(ty - py)) in [(2,1), (1,2)]
    
    elif piece_type == 'k':
        return abs(tx - px) <= 1 and abs(ty - py) <= 1
    
    elif piece_type == 'b':
        if abs(tx - px) != abs(ty - py):
            return False
        dx = 1 if tx > px else -1
        dy = 1 if ty > py else -1
        x, y = px + dx, py + dy
        while (x, y) != (tx, ty):
            if board[x, y] != '':
                return False
            x += dx
            y += dy
        return True
    
    elif piece_type == 'r':
        if tx != px and ty != py:
            return False
        if tx == px:
            step = 1 if ty > py else -1
            for y in range(py + step, ty, step):
                if board[px, y] != '':
                    return False
        else:
            step = 1 if tx > px else -1
            for x in range(px + step, tx, step):
                if board[x, py] != '':
                    return False
        return True
    
    elif piece_type == 'q':
        return can_piece_reach(board, piece_pos, target_pos, 'b', color) or \
               can_piece_reach(board, piece_pos, target_pos, 'r', color)
    
    return False

def is_square_attacked(board, square, by_color):
    for x in range(board.shape[0]):
        for y in range(board.shape[1]):
            piece = board[x, y]
            if piece != '' and piece[-1] == by_color:
                if can_piece_reach(board, (x, y), square, piece[0], by_color):
                    return True
    return False

def generate_moves(board, color, **kwargs):
    upgrades = []
    captures = []
    normal = []
    
    pawn_direction = kwargs.get("pawn_direction", 1)
    
    for x in range(board.shape[0]):
        for y in range(board.shape[1]):
            piece = board[x, y]
            if piece == '' or piece[-1] != color:
                continue
            
            piece_type = piece[0]
            
            if piece_type == 'p':
                nx = x + pawn_direction
                
                if 0 <= nx < board.shape[0]:
                    if board[nx, y] == '':
                        move = ((x, y), (nx, y))
                        if nx == 0 or nx == board.shape[0] - 1:
                            upgrades.append(move)
                        else:
                            normal.append(move)
                    
                    for dy in [-1, 1]:
                        ny = y + dy
                        if 0 <= ny < board.shape[1]:
                            target = board[nx, ny]
                            if target != '' and target[-1] != color:
                                move = ((x, y), (nx, ny))
                                if nx == 0 or nx == board.shape[0] - 1:
                                    upgrades.append(move)
                                else:
                                    captures.append((move, get_piece_value(target[0])))
            
            elif piece_type == 'n':
                for dx, dy in [(2,1), (2,-1), (-2,1), (-2,-1), (1,2), (1,-2), (-1,2), (-1,-2)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < board.shape[0] and 0 <= ny < board.shape[1]:
                        target = board[nx, ny]
                        if target == '':
                            normal.append(((x, y), (nx, ny)))
                        elif target[-1] != color:
                            captures.append((((x, y), (nx, ny)), get_piece_value(target[0])))
            
            elif piece_type == 'b':
                for dx, dy in [(1,1), (1,-1), (-1,1), (-1,-1)]:
                    for dist in range(1, board.shape[0]):
                        nx, ny = x + dx*dist, y + dy*dist
                        if not (0 <= nx < board.shape[0] and 0 <= ny < board.shape[1]):
                            break
                        target = board[nx, ny]
                        if target == '':
                            normal.append(((x, y), (nx, ny)))
                        else:
                            if target[-1] != color:
                                captures.append((((x, y), (nx, ny)), get_piece_value(target[0])))
                            break
            
            elif piece_type == 'r':
                for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                    for dist in range(1, board.shape[0]):
                        nx, ny = x + dx*dist, y + dy*dist
                        if not (0 <= nx < board.shape[0] and 0 <= ny < board.shape[1]):
                            break
                        target = board[nx, ny]
                        if target == '':
                            normal.append(((x, y), (nx, ny)))
                        else:
                            if target[-1] != color:
                                captures.append((((x, y), (nx, ny)), get_piece_value(target[0])))
                            break
            
            elif piece_type == 'q':
                for dx, dy in [(1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]:
                    for dist in range(1, board.shape[0]):
                        nx, ny = x + dx*dist, y + dy*dist
                        if not (0 <= nx < board.shape[0] and 0 <= ny < board.shape[1]):
                            break
                        target = board[nx, ny]
                        if target == '':
                            normal.append(((x, y), (nx, ny)))
                        else:
                            if target[-1] != color:
                                captures.append((((x, y), (nx, ny)), get_piece_value(target[0])))
                            break
            
            elif piece_type == 'k':
                for dx, dy in [(1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < board.shape[0] and 0 <= ny < board.shape[1]:
                        target = board[nx, ny]
                        if target == '':
                            normal.append(((x, y), (nx, ny)))
                        elif target[-1] != color:
                            captures.append((((x, y), (nx, ny)), get_piece_value(target[0])))
    
    captures.sort(key=lambda x: x[1], reverse=True)
    capture_moves = [m for m, v in captures]
    
    return upgrades + capture_moves + normal

def negamax(board, depth, alpha, beta, side, deadline, **kwargs):
    if time.monotonic() >= deadline:
        raise TimeUp
    
    sign = 1 if side == 'w' else -1
    
    if depth <= 0:
        return sign * evaluate_board(board)
    
    moves = generate_moves(board, side, **kwargs)
    if not moves:
        return sign * evaluate_board(board)
    
    best = -INF
    next_side = 'b' if side == 'w' else 'w'
    
    for move in moves:
        child = apply_move(board, move)
        score = -negamax(child, depth - 1, -beta, -alpha, next_side, deadline, **kwargs)
        
        best = max(best, score)
        alpha = max(alpha, score)
        
        if alpha >= beta:
            break
    
    return best

def find_best_move(board, side, depth, deadline, **kwargs):
    moves = generate_moves(board, side, **kwargs)
    
    if not moves:
        return None
    
    best_move = moves[0]
    best_score = -INF
    alpha = -INF
    beta = INF
    next_side = 'b' if side == 'w' else 'w'
    
    for move in moves:
        if time.monotonic() >= deadline:
            raise TimeUp
        
        child = apply_move(board, move)
        
        (fx, fy), (tx, ty) = move
        my_piece = board[fx, fy]
        my_value = get_piece_value(my_piece[0])
        enemy_color = 'b' if side == 'w' else 'w'
        
        bonus = 0
        if is_square_attacked(child, (tx, ty), enemy_color):
            target = board[tx, ty]
            if target != '':
                capture_value = get_piece_value(target[0])
                if capture_value < my_value:
                    bonus = -100
            else:
                bonus = -50
        
        score = -negamax(child, depth - 1, -beta, -alpha, next_side, deadline, **kwargs) + bonus
        
        if score > best_score:
            best_score = score
            best_move = move
        
        alpha = max(alpha, score)
    
    return best_move

def chess_bot(player_sequence, board, time_budget, **kwargs):
    if time_budget <= 0:
        return (0, 0), (0, 0)
    
    color = player_sequence[1]
    deadline = time.monotonic() + max(0, time_budget - 0.05)
    
    moves = generate_moves(board, color, **kwargs)
    if not moves:
        return (0, 0), (0, 0)
    
    for move in moves:
        (x, y), (nx, ny) = move
        target = board[nx, ny]
        if target != '' and target[0] == 'k' and target[-1] != color:
            return move
    
    best_move = moves[0]
    
    try:
        for depth in range(1, 100):
            if time.monotonic() >= deadline:
                raise TimeUp
            
            move = find_best_move(board, color, depth, deadline, **kwargs)
            if move:
                best_move = move
    except TimeUp:
        pass
    
    return best_move

register_chess_bot("SYNTAX", chess_bot)