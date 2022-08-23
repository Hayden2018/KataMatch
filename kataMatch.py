import subprocess
from subprocess import PIPE, DEVNULL
import json
from time import sleep, time

default_cfg = {
  'size': 19,
  'komi': 6.5,
  'handicap': 0,
  'rules': 'tromp-taylor'
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


def match(engine_path, black_cfg, white_cfg, n, game_cfg=default_cfg, logging=True, switch=True):
  black_engine = subprocess.Popen([engine_path, 'analysis', '-config', 'analysis_example.cfg',  '-model', black_cfg['weight']], stdin=PIPE, stdout=PIPE, stderr=DEVNULL)
  white_engine = subprocess.Popen([engine_path, 'analysis', '-config', 'analysis_example.cfg',  '-model', white_cfg['weight']], stdin=PIPE, stdout=PIPE, stderr=DEVNULL)

  sleep(3)
  record = []
  result = {
    'black': 0,
    'white': 0
  }

  k = 0
  if switch and game_cfg['komi'] > 0:
    k = n // 2
    n = n - k

  for j in range(n):

    black_pass = False
    white_pass = False
    data = None

    initial = []
    moves = []

    while (not black_pass) or (not white_pass):

      black_engine.stdin.write(__create_query(black_cfg['visit'], initial, moves, game_cfg).encode())
      black_engine.stdin.flush()
      out = black_engine.stdout.readline()
      m, data = __get_data(out)
      moves.append(['b', m])
      black_pass = True if m == 'pass' else False

      white_engine.stdin.write(__create_query(white_cfg['visit'], initial, moves, game_cfg).encode())
      white_engine.stdin.flush()
      out = white_engine.stdout.readline()
      m, data = __get_data(out)
      moves.append(['w', m])
      white_pass = True if m == 'pass' else False

    if data['moveInfos'][0]['winrate'] > 0.5:
      result['black'] += 1
      record.append(('black_engine', False))
      if logging:
        print('Match', j + 1)
        print('Black Engine Win')
    else:
      result['white'] += 1
      record.append(('white_engine', False))
      if logging:
        print('Match', j + 1)
        print('White Engine Win')

  if not (switch and game_cfg['komi'] > 0):
    result['record'] = record
    return result

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
      moves.append(['b', m])
      white_pass = True if m == 'pass' else False

      black_engine.stdin.write(__create_query(black_cfg['visit'], initial, moves, game_cfg).encode())
      black_engine.stdin.flush()
      out = black_engine.stdout.readline()
      m, data = __get_data(out)
      moves.append(['w', m])
      black_pass = True if m == 'pass' else False

    if data['moveInfos'][0]['winrate'] > 0.5:
      result['white'] += 1
      record.append(('white_engine', True))
      if logging:
        print('Match', n + j + 1)
        print('White Engine Win')
    else:
      result['black'] += 1
      record.append(('black_engine', True))
      if logging:
        print('Match', n + j + 1)
        print('Black Engine Win')
  
  result['record'] = record
  return result


if __name__ == '__main__':

  black_cfg = {
    'weight': 'katago-v1.10.0\kata1-b10c128-11500.txt.gz',
    'visit': 24
  }

  white_cfg = {
    'weight': 'katago-v1.10.0\kata1-b10c128-11500.txt.gz',
    'visit': 12
  }

  engine_path = 'katago-v1.10.0\katago.exe'

  result = match(engine_path, black_cfg, white_cfg, 10, switch=True)
  print(result)