## **Usage**
This python function automatically conduct games between two kataGo engine. Copy to your project folder and import the function as follow

```
from kataMatch import match
```

## **Parameters** 
```
match(engine_path, black_cfg, white_cfg, cfg_path=None, n=10, game_cfg=default_cfg, log=True, switch=False)
```

- **engine_path** - Absolute or relative path string to your katago.exe engine executable
- **black_cfg / white_cfg** - Dictionary containing the following engine configuration for black and white
```
{
    'weight': 'path\to\katago\weight_file.txt.gz',
    'visit': number of visits per move
}
```
- **cfg_path (optional)** - Absolute or relative path string to your analysis configuration file. If unspecified it is assumed to be the default config file in same directory as the engine
- **n (optional)** - Number of games to play with default to 10
- **game_cfg (optional)** - Dictionary representing the game configuration. Key *komi* can be any integer or half integer between [-150, 150]. Key *handicap* must be integer betweem [0, 9]. Key *rules* can be any one of *chinese / japanese / tromp-taylor*. If not provided the following will be used as default
```
{
    'komi': 7.5,
    'handicap': 0,
    'rules': 'chinese'
}
```

- **log (optional)** - Enable console logging after each game is finished with default to True
- **switch (optional)** - Switch side for black and white engine in half of the game if set to True. This value is ignored if the handicap value in game config is non-zero where no switching will occur


## **Result**
The match function return one dictionary object as result
```
result = match(engine_path, black_cfg, white_cfg)
```
The returned dictionary take the following format
```
{
   'black': number of wins for black engine
   'white': number of wins for white engine
   'record': [
      [Winning Engine ('B'/'W'), Switched Side (True/Flase)],
      ...
   ]
}
```
