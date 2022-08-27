import subprocess
from subprocess import PIPE, DEVNULL
import json
from time import time
from os import path

default_cfg = {
  'size': 19,
  'komi': 7.5,
  'handicap': 0,
  'rules': 'chinese'
}

def __create_query(visit, initial, moves, game_cfg):
  return json.dumps({
    'id': str(time()),
    'initialStones': initial,
    "moves": moves,
    'rules': game_cfg['rules'],
    'komi': game_cfg['komi'],
    'boardXSize': game_cfg['size'],
    'boardYSize': game_cfg['size'],
    'maxVisits': visit
  }) + '\n'

def __get_data(out):
  out = out.decode()
  data = json.loads(out)
  m = data['moveInfos'][0]['move']
  return m, data

def __get_initial(handicap):
  stones = []
  if handicap >= 2:
    stones.append(['B', 'Q16'])
    stones.append(['B', 'D4'])
  if handicap >= 3:
    stones.append(['B', 'D16'])
  if handicap >= 4:
    stones.append(['B', 'D16'])
  if handicap >= 5:
    stones.append(['B', 'K10'])
  if handicap >= 6:
    stones.pop()
    stones.append(['B', 'D10'])
    stones.append(['B', 'Q10'])
  if handicap >= 7:
    stones.append(['B', 'Q10'])
  if handicap >= 8:
    stones.pop()
    stones.append(['B', 'K16'])
    stones.append(['B', 'K4'])
  if handicap >= 8:
    stones.append(['B', 'K10'])
  return stones


def match(engine_path, black_cfg, white_cfg, config_path=None, n=10, game_cfg=default_cfg, logging=True, switch=False):

  default_cfg.update(game_cfg)
  game_cfg = default_cfg

  if config_path is None:
    config_path = path.join(path.dirname(engine_path), 'analysis_example.cfg')

  black_engine = subprocess.Popen([engine_path, 'analysis', '-config', config_path, '-model', black_cfg['weight']], stdin=PIPE, stdout=PIPE, stderr=DEVNULL)
  white_engine = subprocess.Popen([engine_path, 'analysis', '-config', config_path, '-model', white_cfg['weight']], stdin=PIPE, stdout=PIPE, stderr=DEVNULL)

  record = []
  result = {
    'black': 0,
    'white': 0
  }

  k = 0
  with_handicap = game_cfg['handicap'] >= 2
  if switch and not with_handicap:
    k = n // 2
    n = n - k

  for j in range(n):

    black_pass = False
    white_pass = False
    data = None

    initial = __get_initial(game_cfg['handicap'])
    moves = []

    while (not black_pass) or (not white_pass):

      if with_handicap:

        white_engine.stdin.write(__create_query(white_cfg['visit'], initial, moves, game_cfg).encode())
        white_engine.stdin.flush()
        out = white_engine.stdout.readline()
        m, data = __get_data(out)
        moves.append(['W', m])
        white_pass = True if m == 'pass' else False

        black_engine.stdin.write(__create_query(black_cfg['visit'], initial, moves, game_cfg).encode())
        black_engine.stdin.flush()
        out = black_engine.stdout.readline()
        m, data = __get_data(out)
        moves.append(['B', m])
        black_pass = True if m == 'pass' else False

      else:

        black_engine.stdin.write(__create_query(black_cfg['visit'], initial, moves, game_cfg).encode())
        black_engine.stdin.flush()
        out = black_engine.stdout.readline()
        m, data = __get_data(out)
        moves.append(['B', m])
        black_pass = True if m == 'pass' else False

        white_engine.stdin.write(__create_query(white_cfg['visit'], initial, moves, game_cfg).encode())
        white_engine.stdin.flush()
        out = white_engine.stdout.readline()
        m, data = __get_data(out)
        moves.append(['W', m])
        white_pass = True if m == 'pass' else False

    if data['moveInfos'][0]['winrate'] > 0.5:
      result['black'] += 1
      record.append(('B', False))
      if logging:
        print('Match', j + 1)
        print('Black Engine Win')
    else:
      result['white'] += 1
      record.append(('W', False))
      if logging:
        print('Match', j + 1)
        print('White Engine Win')

  # Play with black and white reversed
  for j in range(k):

    black_pass = False
    white_pass = False
    data = None

    initial = []
    moves = []

    while (not black_pass) or (not white_pass):

      white_engine.stdin.write(__create_query(white_cfg['visit'], initial, moves, game_cfg).encode())
      white_engine.stdin.flush()
      out = white_engine.stdout.readline()
      m, data = __get_data(out)
      moves.append(['B', m])
      white_pass = True if m == 'pass' else False

      black_engine.stdin.write(__create_query(black_cfg['visit'], initial, moves, game_cfg).encode())
      black_engine.stdin.flush()
      out = black_engine.stdout.readline()
      m, data = __get_data(out)
      moves.append(['w', m])
      black_pass = True if m == 'pass' else False

    if data['moveInfos'][0]['winrate'] > 0.5:
      result['white'] += 1
      record.append(('W', True))
      if logging:
        print('Match', n + j + 1)
        print('White Engine Win')
    else:
      result['black'] += 1
      record.append(('B', True))
      if logging:
        print('Match', n + j + 1)
        print('Black Engine Win')
  
  result['record'] = record
  return result


if __name__ == '__main__':

  black_cfg = {
    'weight': '.\katago-v1.10.0\kata1-b10c128-11500.txt.gz',
    'visit': 18
  }

  white_cfg = {
    'weight': '.\katago-v1.10.0\kata1-b10c128-11500.txt.gz',
    'visit': 12
  }

  engine_path = '.\katago-v1.10.0\katago.exe'

  result = match(engine_path, black_cfg, white_cfg, switch=True)
  print(result)