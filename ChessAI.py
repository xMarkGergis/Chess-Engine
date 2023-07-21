import random

piece_score = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}

knight_score = [[1, 1, 1, 1, 1, 1, 1, 1], # knights are more valuable when placed near the center
                [1, 2, 2, 2, 2, 2, 2, 1], # as then, the knight will be able to attack more squares
                [1, 2, 3, 3, 3, 3, 2, 1], # rather than being on the rim of the board, the knight's options are limited
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]]

bishop_score = [[4, 3, 2, 1, 1, 2, 3, 4], # any of the four bishops will have more of an impact if it goes along a major
                [3, 4, 3, 2, 2, 3, 4, 3], # diagonal. it will control more of the board. if not the main two diagonals,
                [2, 3, 4, 3, 3, 4, 3, 2], # the other ones are fine, but fewer points will be rewarded to the engine
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [4, 3, 1, 1, 1, 2, 3, 4]]

queen_score =  [[1, 1, 1, 3, 1, 1, 1, 1], # similar to knight, centralize the queen as much as possible, more squares
                [1, 2, 3, 3, 3, 1, 1, 1], # for the queen to attack then being on the rim of the board
                [1, 4, 3, 3, 3, 4, 2, 1],
                [1, 2, 3, 3, 3, 2, 2, 1],
                [1, 2, 3, 3, 3, 2, 2, 1],
                [1, 4, 3, 3, 3, 4, 1, 1],
                [1, 1, 2, 3, 3, 1, 1, 1],
                [1, 1, 1, 3, 1, 1, 1, 1]]

rook_score =   [[4, 3, 4, 4, 4, 4, 3, 4], # more pressure is applied when you get your rook on the opponents backside
                [4, 4, 4, 4, 4, 4, 4, 4], # allows you to take their pawns, but also have it on your central back side is
                [1, 1, 2, 3, 3, 2, 1, 1], # good too
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 1, 2, 3, 3, 2, 1, 1],
                [4, 4, 4, 4, 4, 4, 4, 4],
                [4, 3, 4, 4, 4, 4, 3, 4]]

white_pawn_score =  [[8, 8, 8, 8, 8, 8, 8, 8], # pawn promotion is preferable, center control in a chess game is very
                     [8, 8, 8, 8, 8, 8, 8, 8], # important the more centralized you are, the better position you are in
                     [5, 6, 6, 7, 7, 6, 6, 5], # engine will advance pawns a bit more due to this
                     [1, 3, 3, 5, 5, 3, 3, 2],
                     [1, 2, 3, 4, 4, 3, 2, 1],
                     [1, 1, 2, 3, 3, 2, 1, 1],
                     [1, 1, 1, 0, 0, 1, 1, 1],
                     [0, 0, 0, 0, 0, 0, 0, 0]]

black_pawn_score =  [[0, 0, 0, 0, 0, 0, 0, 0],
                     [1, 1, 1, 0, 0, 1, 1, 1],
                     [1, 1, 2, 3, 3, 2, 1, 1],
                     [1, 2, 3, 4, 4, 3, 2, 1],
                     [2, 3, 3, 5, 5, 3, 3, 2],
                     [5, 6, 6, 7, 7, 6, 6, 5],
                     [8, 8, 8, 8, 8, 8, 8, 8],
                     [8, 8, 8, 8, 8, 8, 8, 8]]

piece_position_scores = {"N": knight_score, "B": bishop_score, "Q": queen_score, "R": rook_score,
                         "bp": black_pawn_score, "wp": white_pawn_score}


CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3

'''
picks and returns a random move
'''


def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves) - 1)]


'''
find the best move based on material alone
'''


def find_best_move_minmax_no_recursion(gs, valid_moves):
    turn_multiplier = 1 if gs.WhiteToMove else -1
    opponent_minmax_score = CHECKMATE
    best_move = None
    random.shuffle(valid_moves)
    for player_move in valid_moves:
        gs.make_move(player_move)
        opponents_moves = gs.get_valid_moves()  # get opponents moves
        if gs.stale_mate:
            opponent_max_score = STALEMATE
        elif gs.check_mate:
            opponent_max_score = -CHECKMATE
        else:
            opponent_max_score = -CHECKMATE
            for opponents_move in opponents_moves:  # try to find highest value/best opponent move
                gs.make_move(opponents_move)
                gs.get_valid_moves()
                if gs.check_mate:
                    score = CHECKMATE
                elif gs.stale_mate:
                    score = STALEMATE
                else:
                    score = -turn_multiplier * score_material(
                        gs.board)  # get the highest score possible based on material
                if score > opponent_max_score:
                    opponent_max_score = score
                gs.undo_move()
        if opponent_max_score < opponent_minmax_score:  # if opponents max score is less than previous move
            opponent_minmax_score = opponent_max_score  # it now becomes my best new move
            best_move = player_move
        gs.undo_move()
    return best_move


def find_best_move(gs, valid_moves, return_queue):
    global next_move, counter
    next_move = None
    random.shuffle(valid_moves)
    counter = 0
    # find_move_minmax(gs, valid_moves, DEPTH, gs.WhiteToMove)
    # find_move_negamax(gs, valid_moves, DEPTH, 1 if gs.WhiteToMove else -1)
    find_move_negamax_alphabeta(gs, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.WhiteToMove else -1)
    print(counter)
    return_queue.put(next_move) # whenever its finished put it into return queue


def find_move_minmax(gs, valid_moves, depth, WhiteToMove):
    global next_move
    if depth == 0:
        return score_material(gs.board)

    if WhiteToMove:
        max_score = -CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = find_move_minmax(gs, next_moves, depth - 1, False)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return max_score

    else:
        min_score = CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = find_move_minmax(gs, next_moves, depth - 1, True)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move
                gs.undo_move()
        return min_score


def find_move_negamax(gs, valid_moves, depth, turn_multiplier):
    global next_move, counter
    counter += 1
    if depth == 0:
        return turn_multiplier * score_board(gs)

    max_score = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score = -find_move_negamax(gs, next_moves, depth - 1, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo_move()
    return max_score


def find_move_negamax_alphabeta(gs, valid_moves, depth, alpha, beta, turn_multiplier):
    global next_move, counter
    counter += 1
    if depth == 0:
        return turn_multiplier * score_board(gs)

    # move  ordering - implement later
    max_score = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score = -find_move_negamax_alphabeta(gs, next_moves, depth - 1, -beta, -alpha, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
                print(move, score)
        gs.undo_move()
        if max_score > alpha:  # pruning
            alpha = max_score
        if alpha >= beta:
            break
    return max_score


'''
positive score good for white, negative score good for black
'''


def score_board(gs):
    if gs.check_mate:
        if gs.WhiteToMove:
            return -CHECKMATE  # black wins
        else:
            return CHECKMATE  # white wins
    elif gs.stale_mate:
        return STALEMATE

    score = 0  # a perfect game will have 0 score
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                # score it positionally based on which piece it is
                piece_position_score = 0
                if square[1] != "K":
                    if square[1] == "p":
                        piece_position_score = piece_position_scores[square][row][col] # for pawns
                    else:
                        piece_position_score = piece_position_scores[square[1]][row][col] # for all pieces besides wp & bp

                if square[0] == 'w':  # if white has piece advantage game will have positive score
                    score += piece_score[square[1]] + piece_position_score * .1 # access character at square one, whether a pawn, queen, or king etc
                elif square[0] == 'b':  # if black has piece advantage game will have negative score
                    score -= piece_score[square[1]] + piece_position_score * .1
    return score


'''
score the board based on material
'''


def score_material(board):
    score = 0  # a perfect game will have 0 score
    for row in board:
        for square in row:
            if square[0] == 'w':  # if white has piece advantage game will have positive score
                score += piece_score[square[1]]  # access character at square one, whether a pawn, queen, or king etc
            elif square[0] == 'b':  # if black has piece advantage game will have negative score
                score -= piece_score[square[1]]
    return score