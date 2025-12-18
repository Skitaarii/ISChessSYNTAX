import numpy as np
from numpy import random
from Bots.ChessBotList import register_chess_bot

def chess_bot(player_sequence, board, time_budget, **kwargs):
    color = player_sequence[1]
    all_moves = []

    for x in range(board.shape[0]):
        for y in range(board.shape[1]):

            piece = board[x, y]
            if piece == '' or piece[-1] != color:
                continue

            # PAWN
            # --------------------
            if piece[0] == 'p':
                nx = x + kwargs.get("pawn_direction", 1)

                if 0 <= nx < board.shape[0]:
                    if board[nx, y] == '':
                        all_moves.append(((x, y), (nx, y)))

                    if y > 0 and board[nx, y - 1] != '' and board[nx, y - 1][-1] != color:
                        all_moves.append(((x, y), (nx, y - 1)))

                    if y < board.shape[1] - 1 and board[nx, y + 1] != '' and board[nx, y + 1][-1] != color:
                        all_moves.append(((x, y), (nx, y + 1)))

            # KNIGHT
            # --------------------
            elif piece[0] == 'n':
                for dx, dy in [
                    (2,1), (2,-1), (1,2), (-1,2),
                    (-2,1), (-2,-1), (1,-2), (-1,-2)
                ]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < board.shape[0] and 0 <= ny < board.shape[1]:
                        if board[nx, ny] == '' or board[nx, ny][-1] != color:
                            all_moves.append(((x, y), (nx, ny)))

            # BISHOP
            # --------------------
            elif piece[0] == 'b':
                for dx, dy in [(1,1), (1,-1), (-1,1), (-1,-1)]:
                    nx, ny = x + dx, y + dy
                    while 0 <= nx < board.shape[0] and 0 <= ny < board.shape[1]:
                        if board[nx, ny] == '':
                            all_moves.append(((x, y), (nx, ny)))
                        else:
                            if board[nx, ny][-1] != color:
                                all_moves.append(((x, y), (nx, ny)))
                            break
                        nx += dx
                        ny += dy

            # ROOK
            # --------------------
            elif piece[0] == 'r':
                for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                    nx, ny = x + dx, y + dy
                    while 0 <= nx < board.shape[0] and 0 <= ny < board.shape[1]:
                        if board[nx, ny] == '':
                            all_moves.append(((x, y), (nx, ny)))
                        else:
                            if board[nx, ny][-1] != color:
                                all_moves.append(((x, y), (nx, ny)))
                            break
                        nx += dx
                        ny += dy

            # QUEEN
            # --------------------
            elif piece[0] == 'q':
                for dx, dy in [
                    (1,0), (-1,0), (0,1), (0,-1),
                    (1,1), (1,-1), (-1,1), (-1,-1)
                ]:
                    nx, ny = x + dx, y + dy
                    while 0 <= nx < board.shape[0] and 0 <= ny < board.shape[1]:
                        if board[nx, ny] == '':
                            all_moves.append(((x, y), (nx, ny)))
                        else:
                            if board[nx, ny][-1] != color:
                                all_moves.append(((x, y), (nx, ny)))
                            break
                        nx += dx
                        ny += dy

            # KING
            # --------------------
            elif piece[0] == 'k':
                for dx, dy in [
                    (1,0), (-1,0), (0,1), (0,-1),
                    (1,1), (1,-1), (-1,1), (-1,-1)
                ]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < board.shape[0] and 0 <= ny < board.shape[1]:
                        if board[nx, ny] == '' or board[nx, ny][-1] != color:
                            all_moves.append(((x, y), (nx, ny)))

    if all_moves:
        return all_moves[random.randint(len(all_moves))]

    return (0, 0), (0, 0)

register_chess_bot("RandomMover", chess_bot)