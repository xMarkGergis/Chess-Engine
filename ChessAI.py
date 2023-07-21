import random

piece_score = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2

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


def find_best_move(gs, valid_moves):
    global next_move, counter
    next_move = None
    random.shuffle(valid_moves)
    counter = 0
    # find_move_minmax(gs, valid_moves, DEPTH, gs.WhiteToMove)
    # find_move_negamax(gs, valid_moves, DEPTH, 1 if gs.WhiteToMove else -1)
    find_move_negamax_alphabeta(gs, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.WhiteToMove else -1)
    print(counter)
    return next_move


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
    for row in gs.board:
        for square in row:
            if square[0] == 'w':  # if white has piece advantage game will have positive score
                score += piece_score[square[1]]  # access character at square one, whether a pawn, queen, or king etc
            elif square[0] == 'b':  # if black has piece advantage game will have negative score
                score -= piece_score[square[1]]
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