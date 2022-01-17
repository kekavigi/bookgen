import chess
import chess.svg
from chess.engine import SimpleEngine, Limit, Cp
import json


# Const
START_FEN = 'rnbqkb1r/ppp1pppp/5n2/3p4/3P1B2/2N5/PPP1PPPP/R2QKBNR b KQkq - 2 3'
TREE_DEPTH = 4
STOP_SCORE = Cp(500)

# Engine definition
SF_DIR = 'sf/stockfish_14.1_linux_x64_popcnt'
ENGINE = SimpleEngine.popen_uci(SF_DIR)
ENGINE.configure({
    'Hash': 512,
    'Threads': 2
})
ENGINE_LIMIT = Limit(depth=20)


# helper function
def analyse(board, multi_pv):
    pvs = ENGINE.analyse(
        board,
        ENGINE_LIMIT,
        multipv=multi_pv)

    result = []
    for pv in pvs:
        score = pv['score'].white()

        # do not consider clear advantage
        # or clear blunder by opponent
        if score > STOP_SCORE:
            continue

        wdl = score.wdl()

        # get SAN and push
        move = board.san_and_push(pv['pv'][0])
        fen = board.fen()
        # restore board by popping last added move
        _ = board.pop()

        result.append({
            'name': move,
            'fen': fen,
            'win': wdl.wins,
            'draw': wdl.draws,
            'lose': wdl.losses
        })

    return result


count = 0
def extend(trie, depth=0):
    global count
    count+=1
    print(count)

    # make FEN
    board = chess.Board()
    board.set_fen(trie['fen'])

    filename = 'assets/' + board.fen()\
        .replace('/', '-')\
        .replace(' ', '-')+'.svg'
    trie['fen'] = filename

    with open(filename, 'w') as f:
        f.write(chess.svg.board(board))

    if depth == TREE_DEPTH:
        return trie

    multi_pv = 3 if (board.turn == chess.WHITE) else 7
    trie['children'] = analyse(board, multi_pv)

    for e, child in enumerate(trie['children']):
        trie['children'][e] = extend(child, depth+1)
    return trie


board = chess.Board()
board.set_fen(START_FEN)

trie = {
    'name': 'Start',
    'fen': board.fen()
}

extend(trie)

with open("jobava.json", "w") as f:
        f.write(json.dumps(trie))

ENGINE.quit()
