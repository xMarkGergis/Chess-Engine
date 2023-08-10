"""
This is my main driver file. It will be responsible for handling user input and displaying the current game state object
"""

import pygame as p
import ChessEngine
import ChessAI
from multiprocessing import Process, Queue

BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8  # dimensions of a chess board
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15  # for animation
IMAGES = {}

'''
Initialize a global dictionary of images. This will be called only once in main
'''


def load_images():
    pieces = ["wp", "wB", "wQ", "wK", "wN", "wR", "bp", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    # can access an image by saying 'IMAGES['wp']'


'''
The main driver for this code, handles user input and updating the graphics
'''


def main():
    p.init()
    p.display.set_caption("Mark's Chess Engine")
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    move_log_font = p.font.SysFont("Times New Roman", 13, False, False)
    gs = ChessEngine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False
    animate = False
    load_images()
    running = True
    sq_selected = ()  # no square is selected initially, also keeps track of the last click of user
    player_clicks = []  # two tuples, keeps track of player clicks
    game_over = False
    player_one = True  # if the user is playing white, will be true, if AI is playing, will be false
    player_two = False  # if the user is playing black, will be true, if AI is playing, will be false
    ai_thinking = False # true whenever the engine is coming up with a move, false whenever it is not
    move_finder_process = None
    move_undone = False
    while running:
        human_turn = (gs.WhiteToMove and player_one) or (not gs.WhiteToMove and player_two)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handlers
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()  # (x,y) location of mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sq_selected == (row, col) or col >= 8:  # if user clicks same square twice or user clicked mouse log
                        sq_selected = ()  # deselects
                        player_clicks = []  # clears player clicks
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected)  # appends for both 1st and 2nd clicks
                    if len(player_clicks) == 2 and human_turn: # after second click
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                        print(move.get_chess_notation())
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                sq_selected = ()  # reset user clicks
                                player_clicks = []
                        if not move_made:
                            player_clicks = [sq_selected]
            # key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undo_move()
                    move_made = True
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate() # if engine is currently thinking kill the thread, fixes bug that does not let you undo move
                        ai_thinking = False
                    move_undone = True

                if e.key == p.K_r:  # reset whole board when 'r' is pressed
                    gs = ChessEngine.GameState()
                    valid_moves = gs.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()  # reset
                        ai_thinking = False
                    move_undone = True
        # ai move finder
        if not game_over and not human_turn and not move_undone: # and not move_undone fixes bug where if user undo move, engine continues to think despite it
            if not ai_thinking:
                ai_thinking = True
                return_queue = Queue() # will pass data  between threads
                move_finder_process = Process(target=ChessAI.find_best_move, args=(gs, valid_moves, return_queue)) # when process starts, call this function
                move_finder_process.start() # calls find_best_move(gs, valid_moves, return_queue)

            if not move_finder_process.is_alive(): # whether or not engine is still thinking, if thread is alive or not
                ai_move = return_queue.get() # accesses return queue calls get function to give back whatever gets put in return queue
                if ai_move is None:
                    ai_move = ChessAI.find_random_move(valid_moves)
                gs.make_move(ai_move)
                move_made = True
                animate = True
                ai_thinking = False

        if move_made:
            if animate:
                animate_move(gs.MoveLog[-1], screen, gs.board, clock)
            valid_moves = gs.get_valid_moves()
            move_made = False
            animate = False
            move_undone = False # after move is made set to false

        draw_game_state(screen, gs, valid_moves, sq_selected, move_log_font)

        if gs.check_mate or gs.stale_mate:
            game_over = True
            draw_end_game_text(screen,
                               'Stalemate' if gs.stale_mate else 'Black wins by Checkmate!' if gs.WhiteToMove else 'White wins by Checkmate!')

        clock.tick(MAX_FPS)
        p.display.flip()


'''
responsible for all the graphics within a current game state
'''


def draw_game_state(screen, gs, valid_moves, sq_selected, move_log_font):
    draw_board(screen)  # draw squares on the board
    highlight_squares(screen, gs, valid_moves, sq_selected)
    draw_pieces(screen, gs.board)  # draw pieces on top of those squares
    draw_move_log(screen, gs, move_log_font)


'''
Draw the squares on the board. The top left square is always white       
NOTE: draw the squares before the pieces.
'''


def draw_board(screen):
    global colors
    colors = [p.Color("#eeeed2"), p.Color("#769656")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]  # adds row and column, mod it by 2. This will give me the remainder,
            # which will show whether the row and columns remainder is even or odd.
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''
highlight the square selected and moves for piece selected
'''


def highlight_squares(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == ('w' if gs.WhiteToMove else 'b'):  # sq_selected is a piece that can be moved
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # transparency value
            s.fill(p.Color('light yellow'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            # highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col * SQ_SIZE, move.end_row * SQ_SIZE))


'''
Draws the pieces on the board using the current game_state.board
'''


def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # not empty square
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''
draws the move log
'''


def draw_move_log(screen, gs, font):
    move_log_rect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), move_log_rect)
    MoveLog = gs.MoveLog
    move_texts = []
    for i in range(0, len(MoveLog), 2):
        move_string = str(i//2 + 1) + ") " + str(MoveLog[i]) + " " # calls override method
        if i+1 < len(MoveLog): # make sure black made a move
            move_string += str(MoveLog[i+1]) + "  "
        move_texts.append(move_string)

    moves_per_row = 3
    padding = 5
    line_spacing = 2
    textY = padding
    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i+j]
        text_object = font.render(text, True, p.Color('white'))
        text_location = move_log_rect.move(padding, textY)
        screen.blit(text_object, text_location)
        textY += text_object.get_height() + line_spacing


'''
animating a move
'''


def animate_move(move, screen, board, clock):
    global colors
    coords = []  # list of coordinates that the animations will move through
    dR = move.end_row - move.start_row
    dC = move.end_col - move.start_col
    frames_per_square = 3  # frames to move one square
    frame_count = (abs(dR) + abs(dC)) * frames_per_square
    for frame in range(frame_count + 1):
        r, c = (move.start_row + dR * frame / frame_count, move.start_col + dC * frame / frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col * SQ_SIZE, move.end_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)
        # draw captured piece onto rectangle
        if move.piece_captured != '--':
            if move.enpassant_move:
                enpassant_row = move.end_row + 1 if move.piece_captured[0] == 'b' else move.end_row - 1
                end_square = p.Rect(move.end_col * SQ_SIZE, enpassant_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.piece_captured], end_square)
        # draw moving piece
        screen.blit(IMAGES[move.piece_moved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def draw_end_game_text(screen, text):
    font = p.font.SysFont("Helvitca", 36, True, False)
    text_object = font.render(text, 0, p.Color('White'))
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - text_object.get_width() / 2,
                                                                 BOARD_HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, 0, p.Color("Black"))
    screen.blit(text_object, text_location.move(2, 2))


if __name__ == "__main__":
    main()
