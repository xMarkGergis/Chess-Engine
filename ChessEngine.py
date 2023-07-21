"""
I will have this class store all the information about the current state of the game. Also, it will determine the valid
moves at any given state as well as keep a move log.
"""


class GameState:
    def __init__(self):
        # the first character represents the color of the piece, 'b' or 'w'
        # the second character represents the type of the piece, 'K (king)', 'Q','B','R','N (knight)' or 'p'.
        # "--" represents an empty space with no piece.
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.move_functions = {'p': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves,
                               'B': self.get_bishop_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}

        self.WhiteToMove = True
        self.MoveLog = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.check_mate = False  # no valid squares for king and in check
        self.stale_mate = False  # no valid squares for king and not in check
        self.enpassant_possible = ()  # x,y for the square where en passant is possible
        self.current_castling = CastleRights(True, True, True, True)
        self.castle_log = [CastleRights(self.current_castling.wks, self.current_castling.bks,
                                        self.current_castling.wqs, self.current_castling.bqs)]

    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.MoveLog.append(move)  # log move in order to be able to undo later
        self.WhiteToMove = not self.WhiteToMove
        # update kings location if it is moved
        if move.piece_moved == 'wK':
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.black_king_location = (move.end_row, move.end_col)

        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'

        if move.enpassant_move:
            self.board[move.start_row][move.end_col] = '--'  # capturing the pawn

        # update enpassant possible variable
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:  # only on two square pawn advances
            self.enpassant_possible = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.enpassant_possible = ()

        if move.castle_move:
            if move.end_col - move.start_col == 2:  # king side castle move, king moved to king side
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = '--'  # erase olf rook
            else:  # queen side castle move, king moved to queen side
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]
                self.board[move.end_row][move.end_col - 2] = '--'

        # update castle rights variable
        self.update_castle_rights(move)
        self.castle_log.append(CastleRights(self.current_castling.wks, self.current_castling.bks,
                                            self.current_castling.wqs, self.current_castling.bqs))

    '''
    undo the last move made
    '''

    def undo_move(self):
        if len(self.MoveLog) != 0:
            move = self.MoveLog.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.WhiteToMove = not self.WhiteToMove  # switch turns back

            if move.piece_moved == 'wK':
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == 'bK':
                self.black_king_location = (move.start_row, move.start_col)

            if move.enpassant_move:
                self.board[move.end_row][move.end_col] = '--'  # leave landing square blank
                self.board[move.start_row][move.end_col] = move.piece_captured
                self.enpassant_possible = (move.end_row, move.end_col)

            if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
                self.enpassant_possible = ()

            self.castle_log.pop()  # get rid of the new castle rights from the move that's being undone
            self.current_castling = self.castle_log[-1]  # set current castle rights to the last one in the list

            if move.castle_move:
                if move.end_col - move.start_col == 2:  # king side
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = '--'
                else:  # queen side
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = '--'

            self.check_mate = False;
            self.stale_mate = False;

    '''
    update the castle rights given the move
    '''

    def update_castle_rights(self, move):
        if move.piece_moved == 'wK':
            self.current_castling.wks = False
            self.current_castling.wqs = False
        elif move.piece_moved == 'bK':
            self.current_castling.bks = False
            self.current_castling.bqs = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:  # left rook
                    self.current_castling.wqs = False
                elif move.start_col == 7:  # right rook
                    self.current_castling.wks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:  # left rook
                    self.current_castling.bqs = False
                elif move.start_col == 7:  # right rook
                    self.current_castling.bks = False

    '''
    all moves considering possible checks
    '''

    def get_valid_moves(self):
        temp_enpassant_possible = self.enpassant_possible
        # copy current castling
        temp_current_castling = CastleRights(self.current_castling.wks, self.current_castling.bks,
                                             self.current_castling.wqs, self.current_castling.bqs)
        moves = self.all_possible_moves()  # generates possible move
        if self.WhiteToMove:
            self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves)
        else:
            self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves)
        for i in range(len(moves) - 1, -1, -1):  # reverse order
            self.make_move(moves[i])
            self.WhiteToMove = not self.WhiteToMove  # for each of opponents move see if king is attacked
            if self.in_check():
                moves.remove(moves[i])  # if opponent attacks king not valid move
            self.WhiteToMove = not self.WhiteToMove
            self.undo_move()
        if len(moves) == 0:  # counts as either checkmate or stalemate
            if self.in_check():
                self.check_mate = True
            else:
                self.stale_mate = True
        else:
            self.check_mate = False
            self.stale_mate = False

        self.enpassant_possible = temp_enpassant_possible
        self.current_castling = temp_current_castling
        return moves

    '''
    determine if current player is in check
    '''

    def in_check(self):
        if self.WhiteToMove:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])

    '''
    determine if enemy can attack the square r, c
    '''

    def square_under_attack(self, r, c):
        self.WhiteToMove = not self.WhiteToMove  # switch to opponents pov
        enemy_moves = self.all_possible_moves()
        self.WhiteToMove = not self.WhiteToMove  # switch back
        for move in enemy_moves:
            if move.end_row == r and move.end_col == c:  # if under attack
                return True
        return False

    '''
    all moves without considering checks
    '''

    def all_possible_moves(self):
        moves = []
        for r in range(len(self.board)):  # num of rows
            for c in range(len(self.board[r])):  # num of cols in given row
                turn = self.board[r][c][0]
                if (turn == 'w' and self.WhiteToMove) or (turn == 'b' and not self.WhiteToMove):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c,
                                               moves)  # based on each move it will call the move function for each
        return moves

    '''
    adds all the pawn moves for the pawn located at row and col to the list
    '''

    def get_pawn_moves(self, r, c, moves):
        if self.WhiteToMove:  # white pawn moves
            if self.board[r - 1][c] == "--":
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":  # 2 square pawn advance
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:  # make sure to not go to col -1
                if self.board[r - 1][c - 1][0] == 'b':  # enemy piece to capture
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, enpassant_move=True))
            if c + 1 <= 7:  # captures to the right
                if self.board[r - 1][c + 1][0] == 'b':  # enemy piece to capture
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, enpassant_move=True))
        else:  # black pawn moves
            if self.board[r + 1][c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":  # 2 square pawn advance
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:  # make sure to not go to col -1
                if self.board[r + 1][c - 1][0] == 'w':  # enemy piece to capture
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, enpassant_move=True))
            if c + 1 <= 7:  # captures to the right
                if self.board[r + 1][c + 1][0] == 'w':  # enemy piece to capture
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, enpassant_move=True))

    '''
    adds all the rook moves for the rook located at row and col to the list
    '''

    def get_rook_moves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right
        enemy_color = "b" if self.WhiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:  # num on board
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":  # empty space valid
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:  # enemy piece valid
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:  # friendly piece invalid
                        break
                else:  # off board
                    break

    '''
    adds all the knight moves for the knight located at row and col to the list
    '''

    def get_knight_moves(self, r, c, moves):
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        friend_color = "w" if self.WhiteToMove else "b"
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != friend_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    '''
    adds all the bishop moves for the bishop located at row and col to the list
    '''

    def get_bishop_moves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # similar to rook movement, diagonal directions instead
        enemy_color = "b" if self.WhiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:  # num on board
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":  # empty space valid
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:  # enemy piece valid
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:  # friendly piece invalid
                        break
                else:  # off board
                    break

    '''
    adds all the queen moves for the queen located at row and col to the list
    '''

    def get_queen_moves(self, r, c, moves):  # queen has power of both rook and bishop movement
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    '''
    adds all the king moves for the king located at row and col to the list
    '''

    def get_king_moves(self, r, c, moves):
        king_moves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        friend_color = "w" if self.WhiteToMove else "b"
        for i in range(8):
            end_row = r + king_moves[i][0]
            end_col = c + king_moves[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != friend_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    '''
    generate all valid castle moves for the king then adds those moves to the list of moves
    '''

    def get_castle_moves(self, r, c, moves):
        if self.square_under_attack(r, c):
            return  # cannot castle if in check
        if (self.WhiteToMove and self.current_castling.wks) or (not self.WhiteToMove and self.current_castling.bks):
            self.get_kingside_castle_moves(r, c, moves)
        if (self.WhiteToMove and self.current_castling.wqs) or (not self.WhiteToMove and self.current_castling.bqs):
            self.get_queenside_castle_moves(r, c, moves)

    def get_kingside_castle_moves(self, r, c, moves):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if not self.square_under_attack(r, c + 1) and not self.square_under_attack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, castle_move=True))

    def get_queenside_castle_moves(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--' and \
         not self.square_under_attack(r, c - 1) and not self.square_under_attack(r, c - 2):
            moves.append(Move((r, c), (r, c - 2), self.board, castle_move=True))


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    # maps keys to values
    # key : value
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, enpassant_move=False, castle_move=False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.is_pawn_promotion = (self.piece_moved == 'wp' and self.end_row == 0) or (
                self.piece_moved == 'bp' and self.end_row == 7)
        self.enpassant_move = enpassant_move
        if self.enpassant_move:
            self.piece_captured = 'wp' if self.piece_moved == 'bp' else 'bp'

        self.castle_move = castle_move
        self.is_captured = self.piece_captured != "--"

        self.MoveID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    '''
    overriding the eq method 
    '''

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.MoveID == other.MoveID
        return False

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]

    # overriding the str() function
    def __str__(self):
        # castle moves
        if self.castle_move:
            return "O-O" if self.end_col == 6 else "O-O-O"

        end_square = self.get_rank_file(self.end_row, self.end_col)
        # pawn moves
        if self.piece_moved[1] == 'p':
            if self.is_captured:
                return self.cols_to_files[self.start_col] + "x" + end_square
            else:
                return end_square

        # piece moves
        move_string = self.piece_moved[1]
        if self.is_captured:
            move_string += 'x'
        return move_string + end_square
