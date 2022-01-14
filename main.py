import json, requests
import io, chess.pgn

from tqdm import tqdm
from time import sleep


PLAY_AS = 'white'
USER_NAME = 'kekavigi1'
CHESS_RULES = 'chess'         
TIME_CLASS = 'rapid'  # daily, rapid, blitz, bullet
#TIME_CONTROL
IS_RATED = True 

ARCHIVES_URL = f'https://api.chess.com/pub/player/{USER_NAME}/games/archives'


## for extracting data from parsed JSON
def extract_dict(game):
    if (game[PLAY_AS]['username'] != USER_NAME
            or game['rules'] != CHESS_RULES
            or game['rated'] != IS_RATED
            or game['time_class'] != TIME_CLASS):
        return None
    
    # parse PGN string
    pgn_ = io.StringIO(game['pgn'])
    pgn_ = chess.pgn.read_game(pgn_)

    # extract move
    moves = repr(pgn_.mainline())
    moves = moves.split('(')[1].split(')')[-2].split()
    moves = ['Start'] + [move for move in moves if '.' not in move]
    
    # find opening name
    opening = pgn_.headers['ECOUrl']
    opening = opening.split('https://www.chess.com/openings/')[-1]
    opening = opening.replace('-', ' ')
    
    # include link to the game
    link = pgn_.headers['Link']
    
    # find result: this is simple, but isn't accurate
    result = game[PLAY_AS]['result'] == 'win'
    
    return {
        'moves': moves,
        'opening': opening,
        'link': link,
        'result': result}


# for creating Trie in-place
def extend(trie, moves, info):
    now = moves[0]

    # add new node
    if 'name' not in trie:
        trie['name'] = now
        trie['children'] = []
        trie['win'] = 0
        trie['total'] = 0
        trie['opening'] = info['opening']
        trie['link'] = info['link']
    
    # update data
    trie['win'] += info['result']
    trie['total'] += 1
    
    # if that was last element
    if len(moves)==1:
        return trie
    
    # extend Trie
    for e, child in enumerate(trie['children']):
        if child['name'] == moves[1]:
            # pass responsibility to the child
            trie['children'][e] = extend(trie['children'][e], moves[1:], info)
            break
    # make new child
    else: trie['children'].append(extend({}, moves[1:], info))
    return trie


# trim Trie in-place
def trim(trie, to_cut=False):
    if to_cut:
        del trie['children']
        return trie
    
    for e, child in enumerate(trie['children']):
        z = trie['children'][e]

        # trim if there is only 1 game
        trie['children'][e] = trim(z, z['total']==1)
        
        # cleaning unused data
        try: del trie['opening'], trie['link']
        except: pass

    return trie


def main():
    trie = {}

    # get all archived data (by month)
    raw = requests.get(ARCHIVES_URL).text
    archives = json.loads(raw)['archives']

    for month in tqdm(archives):
        raw = requests.get(month).text
        this_month = json.loads(raw)['games']
        
        # extend trie
        for game in this_month:
            z = extract_dict(game)
            if not z: continue
            extend(trie, z['moves'], z)
        
        # respect the server
        sleep(1)
    
    trie = trim(trie)
    
    # saving file
    with open("sample.json", "w") as f:
        f.write(json.dumps(trie))


if __name__ == '__main__':
    main()
