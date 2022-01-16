import io
import requests
import json

import chess
import chess.pgn as PGN

from tqdm import tqdm
from time import sleep

# CONST
USERNAME = 'kekavigi1'
PLAY_AS = 'white'
CHESS_RULES = 'chess'
TIME_CLASS = 'rapid'
IS_RATED = True
TIME_CONTROL = None
ARCHIVES_URL = f'https://api.chess.com/pub/player/{USERNAME}/games/archives'


def extract(game):
    '''Extract relevant informations from JSON.'''

    pgn = PGN.read_game(io.StringIO(game['pgn']))

    opening = pgn\
        .headers['ECOUrl']\
        .split('https://www.chess.com/openings/')[-1]\
        .replace('-', ' ')

    moves = repr(pgn.mainline())\
        .split('(')[1]\
        .split(')')[-2]\
        .split()
    moves = ['Start'] + [move for move in moves if '.' not in move]

    is_play_as_white = pgn.headers['White'] == USERNAME

    if is_play_as_white:
        if pgn.headers['Result'] == '1-0':
            result = 'W'
        elif pgn.headers['Result'] == '0-1':
            result = 'L'
        else:
            result = 'D'
    else:  # USERNAME as Black
        if pgn.headers['Result'] == '1-0':
            result = 'L'
        elif pgn.headers['Result'] == '0-1':
            result = 'W'
        else:
            result = 'D'

    extracted = {
        'url': game['url'],
        'time_control': game['time_control'],
        'time_class': game['time_class'],
        'game_rules': game['rules'],
        'opening_name': opening,
        'moves': moves,
        'result': result,
        'play_as': 'white' if is_play_as_white else 'black'
    }

    return extracted


def extend(trie, game_data, nth=0):

    # add new node
    if 'name' not in trie:
        trie['name'] = game_data['moves'][nth]
        trie['fen'] = game_data['moves'][1:nth+1]
        trie['children'] = []

        # game_data['result']
        trie['win'] = 0
        trie['draw'] = 0
        trie['lose'] = 0

        # another info that maybe deleted later
        trie['url'] = game_data['url']
        trie['opening_name'] = game_data['opening_name']

    # update data
    if game_data['result'] == 'W':
        trie['win'] += 1
    elif game_data['result'] == 'D':
        trie['draw'] += 1
    else:
        trie['lose'] += 1

    # if that was last element
    if nth+1 == len(game_data['moves']):
        return trie

    # extend Trie
    for e, child in enumerate(trie['children']):
        if child['name'] == game_data['moves'][nth+1]:
            # pass responsibility to the child
            trie['children'][e] = extend(trie['children'][e], game_data, nth+1)
            break
    # make new child
    else:
        trie['children'].append(extend({},  game_data, nth+1))
    return trie


def trim(trie, to_cut=False):
    '''Trim unused branch and clean all node'''

    # create FEN
    if isinstance(trie['fen'], list):
        board = chess.Board()
        for move in trie['fen']:
            board.push_san(move)

        filename = 'assets/' + board.fen()\
            .replace('/', '-')\
            .replace(' ', '-')+'.svg'

        with open(filename, 'w') as f:
            f.write(chess.svg.board(board))

        trie['fen'] = filename

    if to_cut:
        # this is leaf
        del trie['children']
        return trie

    for e, child in enumerate(trie['children']):
        # this is branch

        # trim if there is only 1 game
        z = trie['children'][e]
        total_game = z['win'] + z['draw'] + z['lose']
        trie['children'][e] = trim(z, total_game == 1)

        # cleaning unused data
        try:
            del trie['opening_name'],
            del trie['url']
        except:
            pass

    return trie


def main():
    # get all archived data (by month)
    raw = requests.get(ARCHIVES_URL).text
    archives = json.loads(raw)['archives']

    trie = {}

    for month in tqdm(archives):
        # download monthly archive
        raw = ''
        sleep_counter = 1

        while not raw:
            # respect the server
            sleep(sleep_counter)
            sleep_counter *= 2
            raw = requests.get(month).text

        # parse
        this_month = json.loads(raw)['games']

        # extend trie
        for game in this_month:
            g = extract(game)

            # sanity check
            if g['game_rules'] != CHESS_RULES:
                continue
            if g['time_class'] != TIME_CLASS:
                continue
            if g['play_as'] != PLAY_AS:
                continue

            extend(trie, g)

    # trimmed
    trim(trie)

    # saving file
    with open("sample.json", "w") as f:
        f.write(json.dumps(trie))


if __name__ == '__main__':
    main()
