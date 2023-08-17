var board = null
var game = new Chess()
var whiteSquareGrey = '#a9a9a9'
var blackSquareGrey = '#696969'

function removeGreySquares() {
    $('#myBoard .square-55d63').css('background', '')
}

function greySquare(square) {
    var $square = $('#myBoard .square-' + square)

    var background = whiteSquareGrey
    if ($square.hasClass('black-3c85d')) {
        background = blackSquareGrey
    }

    $square.css('background', background)
}

function onDragStart(source, piece) {
    // do not pick up pieces if the game is over
    if (game.game_over()) return false

    // or if it's not that side's turn
    if ((game.turn() === 'w' && piece.search(/^b/) !== -1) ||
        (game.turn() === 'b' && piece.search(/^w/) !== -1)) {
        return false
    }
}

function onDrop(source, target) {
    removeGreySquares()
    // see if the move is legal
    var move = game.move({
        from: source,
        to: target,
        promotion: 'q' // NOTE: always promote to a queen for example simplicity
    })
    // illegal move
    if (move === null) return 'snapback'
    $('.turn').text("AI's  Turn")

    let fenStr = {'fen': game.fen()}
    $('.moves').text(splitHistoryIntoChunks())
    splitHistoryIntoChunks()
    $.ajax({
        type: "POST",
        url: "/api/process_move",
        data: JSON.stringify(fenStr),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        success: function (response) {
            var moving = game.move({
                from: response.start, to: response.end, promotion: 'q',
            })
            board.position(game.fen())
            $('.turn').text("Your Turn")
            if (game.in_check()) {
                $('.check').removeClass('check-king')
            } else {
                $('.check').addClass('check-king')
            }
            $('.moves').text(splitHistoryIntoChunks())


        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.log(textStatus, errorThrown);
        }
    });
    if (game.in_check()) {
        $('.check').removeClass('check-king')
    } else {
        $('.check').addClass('check-king')
    }
}

function onMouseoverSquare(square, piece) {
    // get list of possible moves for this square
    var moves = game.moves({
        square: square,
        verbose: true
    })

    // exit if there are no moves available for this square
    if (moves.length === 0) return
    if (piece[0] == 'w') {
        // highlight the square they moused over
        greySquare(square)
        // highlight the possible squares for this piece
        for (var i = 0; i < moves.length; i++) {
            greySquare(moves[i].to)
        }
    }

}

function onMouseoutSquare(square, piece) {
    removeGreySquares()
}

function onSnapEnd() {
    board.position(game.fen())
}

function unDoBoardButton() {
    console.log("called")
    game.undo()
    game.undo()
    board.position(game.fen())
}


function resetBoardButton() {
    game.reset()
    board.position(game.fen())
}

function splitHistoryIntoChunks() {
    let moveHistStr = ''
    let moveHistory = game.history()
    let chunkSize = 2
    var result = [];
    for (let i = 0; i < moveHistory.length; i += chunkSize) {
        result.push(moveHistory.slice(i, i + chunkSize));
    }
    for (let i = 0; i < result.length; i++) {
        let cr = (i + 1).toString() + ')' + result[i].join(' ') + ' '
        moveHistStr += cr
    }
    return moveHistStr;
}

var config = {
    draggable: true,
    position: 'start',
    showNotation: false,
    onDragStart: onDragStart,
    onDrop: onDrop,
    onMouseoutSquare: onMouseoutSquare,
    onMouseoverSquare: onMouseoverSquare,
    onSnapEnd: onSnapEnd
}
board = Chessboard('myBoard', config)
$('.undo-btn').click(unDoBoardButton)
$('.reset-btn').click(resetBoardButton)