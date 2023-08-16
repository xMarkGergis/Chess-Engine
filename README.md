# Chess-Engine
AI-powered Chess Engine Website here
## Overview
I created this engine due to my passion for the game of Chess and my desire to dive into the world of more advanced Algorithms. During development, I noticed the engine prioritized only pieces over its position in the overall game state, but as I delved deeper, I explored minimax, which left a bit more to be desired, as the time complexity of the engine was not in line with my expectations. Fast forward after the implementation of the NegaMax Algorithm, it gave the engine optimal move selection as now, the number of nodes that need to be evaluated are reduced, leading to faster and more efficient computations. With pruning, the engine now prunes away branches of the game tree that are proven to be irrelevant, which helped me increase the depth of the engine (how many moves it can see ahead) without compromising on time complexity. 

## Features
Castling: Able to perform castling moves on kingside and queenside to add depth to your gameplay.

En Passant: This engine supports en passant moves.

Pawn Promotions: Able to promote your pawn pieces.

Fully Functional Move Log: This engine keeps track of all the moves during the game state using proper chess notation and can be used for review and analysis. 

Undo Move and Reset Board: Easily undo your moves and the engines with 'z' and reset the game by clicking 'r.'

Check and Checkmate: The engine accurately detects check and checkmate situations.

Move Animation and Piece Highlighting: Enjoy visually engaging move animations and highlighting of legal moves.

## How to Use
1. Clone the repository
2. Run 'ChessMain.py' file to start the game

Feel free to report issues and/or provide feedback to enhance the engine further.

## Visuals
![chessex1](https://github.com/xMarkGergis/Chess-Engine/assets/121286835/25f0cc78-1f9d-4cf0-b270-032ba3537a98)
![chessex2](https://github.com/xMarkGergis/Chess-Engine/assets/121286835/fd2fd9a7-2c11-4058-b562-56e39ec00508)
