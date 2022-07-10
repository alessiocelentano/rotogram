import os


PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
SESSION_NAME = 'Rotogram'
PKMN_LIST_PATH = f'{PROJECT_ROOT}/src/pokemon.txt'
with open(PKMN_LIST_PATH) as f:
    POKEMON_LIST = f.read()

CACHE_TIME = 3
MOVE_PER_PAGE = 5
# Key: PokéAPI form name
# Value: Rotogram form name
MAIN_ALTERNATIVE_FORMS = {
    'alola': 'Alolan',
    'galar': 'Galarian',
    'hisui': 'Hisuian',
    'mega': 'Mega',
    'gmax': 'Gigantamax'
}
SHINY_KEYWORD = 'missingno'
SHINY_PAGE_TITLE = 'MissingNo'
SHINY_PAGE_TYPING = 'Bird / Normal'
SHINY_PAGE_THUMB_URL = 'https://archives.bulbagarden.net/media/upload/9/98/Missingno_RB.png'

ZAP = '\u26A1'
TOOL = '\U0001F6E0'
LOADING_CIRCLE = '\U0001F504'
MINUS = '\u2796'
PLUS = '\u2795'
SWORDS = '\u2694'
HOUSE = '\U0001F3E0'
RED_CIRCLE = '\U0001F534'
ORANGE_CIRCLE = '\U0001F7E0'
YELLOW_CIRCLE = '\U0001F7E1'
GREEN_CIRCLE = '\U0001F7E2'
BLUE_CIRCLE = '\U0001F535'
PURPLE_CIRCLE = '\U0001F7E3'
BLACK_CIRCLE = '\u26AB'
RED_SPARK = '\U0001F4A5'
TICK = '\u2705'
X = '\u274C'
HEART = '\u2764'
BACK = '\U0001F519'
SHINE = '\u2728'
SPACE_INVADER = '\U0001F47E'
GLYPH_NOT_FOUND = '\u25A1'
TYPE_EMOJI = {
    'grass': '\U0001F331',
    'fire': '\U0001F525',
    'water': '\U0001F4A7',
    'flying': '\U0001F985',
    'bug': '\U0001F41E',
    'normal': '\U0001F43E',
    'dragon': '\U0001F409',
    'ice': '\u2744',
    'ghost': '\U0001F47B',
    'fighting': '\U0001F4AA',
    'fairy': '\U0001F380',
    'steel': '\u2699',
    'dark': '\U0001F319',
    'psychic': '\U0001F52E',
    'electric': '\u26A1',
    'ground': '\U0001F30D',
    'rock': '\U0001FAA8',
    'poison': '\u2620',
    'bird': '\U0001F426',
    'no': ''
}
