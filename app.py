from multiprocessing import Queue
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from ChessAI import find_best_move
from ChessEngine import GameState
from ChessPackage import ChessAI

app = Flask(__name__, static_url_path="", static_folder="static")
cors = CORS(app)
app.config["SECRET_KEY"] = "secret!"
app.config["CORS_HEADERS"] = "Content-Type"

'''
converts fen string to a board representation
'''

def fen_to_board(fen):  
    board = []
    for row in fen.split("/"):
        brow = []
        for c in row:
            if c == " ":
                break
            elif c in "12345678":
                brow.extend(["--"] * int(c))
            elif c == "p":
                brow.append("bp")
            elif c == "P":
                brow.append("wp")
            elif c > "Z":
                brow.append("b" + c.upper())
            else:
                brow.append("w" + c)

        board.append(brow)
    return board

'''
route to process a move using the ChessAI module
'''

@app.route("/api/process_move", methods=["GET", "POST"])  # using only post method
def process_move():
    content = request.json["fen"]   # extracts FEN string
    board_rep = fen_to_board(content)
    gs = GameState()
    gs.board = board_rep
    gs.WhiteToMove = False
    valid_moves = gs.get_valid_moves()
    return_queue = Queue()
    ChessAI.find_best_move(gs, valid_moves, return_queue)  # calling ChessAI
    ai_move = return_queue.get()    # retrieve AI's move from the queue
    if ai_move: # convert AI move to standard notation
        start = f"{ai_move.cols_to_files[ai_move.start_col]}{ai_move.rows_to_ranks[ai_move.start_row]}"
        end = f"{ai_move.cols_to_files[ai_move.end_col]}{ai_move.rows_to_ranks[ai_move.end_row]}"
        return jsonify({"start": start, "end": end})


@app.route("/")
def home_page():
    return render_template("index.html")


if __name__ == "__main__":
    gs = GameState()
    app.debug = True
    app.run()
