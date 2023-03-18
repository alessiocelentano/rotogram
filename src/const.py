import os
import configparser

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
PKMN_LIST_PATH = f'{PROJECT_ROOT}/src/pokemon.txt'
USER_SETTINGS_PATH = f'{PROJECT_ROOT}/src/user_settings.json'
with open(PKMN_LIST_PATH) as f:
    POKEMON_LIST = f.read()

CONFIG_FILE_NAME = f'{PROJECT_ROOT}/src/config.ini'
CONFIG_SECTION_NAME = 'rotogram'
config = configparser.ConfigParser()
config.read(CONFIG_FILE_NAME)

API_ID = config[CONFIG_SECTION_NAME]['api_id']
API_HASH = config[CONFIG_SECTION_NAME]['api_hash']
BOT_TOKEN = config[CONFIG_SECTION_NAME]['bot_token']
BOT_USERNAME = config[CONFIG_SECTION_NAME]['bot_username']
SESSION_NAME = config[CONFIG_SECTION_NAME]['session_name']

CACHE_TIME = 3
MOVE_PER_PAGE = 5
QUERY_PER_SEARCH = 10
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
BUTTON = '\U0001F518'
EYE = '\U0001F441' + '\uFE0F' + '\u200D' + '\U0001F5E8' + '\uFE0F'
POKEMON = '\U0001F432'
GLOVE = '\U0001F94A'
MOVE_DATA = '\U0001F522'
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
    None: ''
}

START = f'''
{ZAP} <b><u>What is Rotogram?</u></b>
Rotogram is your detailed and always up-to-date Pokémon bot. \
You can check infos about every specie \
as quickly as possible, without ever leaving Telegram

{TOOL} <b><u>Usage</u></b>
Just write Pokemon name after @rotogrambot (e.g.: @rotogrambot Rotom)

@alessiocelentano | \
<a href='t.me/rotogram'>Follow us</a> | \
<a href='github.com/alessiocelentano/rotogram'>GitHub</a>
'''
START_SHINY_UNLOCKED = f'''
{ZAP} <b><u>What is Rotogram?</u></b>
Rotogram is your detailed and always up-to-date Pokémon bot. \
You can check infos about every specie \
as quickly as possible, without ever leaving Telegram

{TOOL} <b><u>Usage</u></b>
Just write Pokemon name after @rotogrambot (e.g.: @rotogrambot Rotom)

{SPACE_INVADER} <b>...?</b>
You have a strange item... it has one command:
/toggle_shiny

@alessiocelentano | \
<a href='t.me/rotogram'>Follow us</a> | \
<a href='github.com/alessiocelentano/rotogram'>GitHub</a>
'''
SHINY_ACCEPTED = f'''
You accepted a strange gift.
It contains a message:

'<i>Yo trainer, try to search some Pokémon on Rotogram with this new item.
It contains a command called /toggle_shiny. Use it on @rotogrambot chat.
Follow me on @rotogram for more news like this.

with {HEART} ,
- the developer</i>'
'''

LOADING = f'{LOADING_CIRCLE}  Loading...'
SHINY_PAGE_LOADING = f'{GLYPH_NOT_FOUND} L?ad?ng...?'
SET_SHINY = f'Shiny thumbnails enabled successfully! {SHINE}'
UNSET_SHINY = f'Shiny thumbnails disabled {X}'
NO_EVOLUTION = '<i>It is not known to evolve into or from any other Pokémon</i>'
POKEMON_NOT_FOUND = 'Ooops! Pokémon not found, try again.'
MOVEPOOL_TITLE = '<a href="{}">{}</a> <u><b>Movepool ({}/{})</b></u>\n'
MOVE = '''
– <b>{name}</b> – (<i>{class}</i>)
<b>Type</b>: {type} {emoji}
<b>Power</b>: {power} | <b>Accuracy</b>: {accuracy}
'''

REDUCE = f'{MINUS}  Reduce'
EXPAND = f'{PLUS}  Expand'
MOVEPOOL = f'{SWORDS}  Moves'
LOCATION = f'{HOUSE}  Locations'
BACK = f'{BACK} Back'
ACCEPT_SHINY_BUTTON = f'{TICK} ACCEPT GIFT'

SHEDINJA_METHOD = '''\
evolve Nincada having one Poké Ball in bag and one empty slot in party
'''
MALAMAR_METHOD = '''\
while the game system is held upside-down
'''
SIRFETCH_METHOD = '''\
land three critical hits in one battle
'''
RUNERIGUS_METHOD = '''\
travel under the stone bridge in Dusty Bowl after taking at least\
49 damage from attacks without fainting
'''
ALCREMIE_METHOD = '''\
while holding a Sweet when its Trainer spins and strikes a pose
'''
URSHIFU_METHOD = '''\
interact with Scroll of Darkness/Waters
'''

POKEMON_PAGE = '''
<b><u>{pokemon_full_name}</u></b> <a href="{artwork_url}">{emoji1}{emoji2}</a>
<b>Type</b>: {typing}
<b>Ability</b>: {abilities}\
{hidden_ability_line}

<b><u>Evolutions</u></b>
{evolution_family}\
{alternative_forms}

<b><u>Base stats</u></b>
{stats}
'''

POKEMON_PAGE_EXPANDED = '''
<b><u>{pokemon_full_name}</u></b> <a href="{artwork_url}">{emoji1}{emoji2}</a>
<b>Type</b>: {typing}
<b>Ability</b>: {abilities}\
{hidden_ability_line}

<b><u>Evolutions</u></b>
{evolution_family}\
{alternative_forms}

<u><b>Pokédex data</b></u>
<b>Species</b>: {genus}
<b>National Pokedex Number</b>: {dex_number}
<b>Height</b>: {height}
<b>Weight</b>: {weight}
<b>Gender (male/female)</b>: {gender_percentage}

<u><b>Game data</b></u>
<b>Base friendship</b>: {base_friendship}
<b>EV yield</b>: {ev_yield}
<b>Catch rate</b>: {catch_rate}
<b>Growth rate</b>: {growth_rate}
<b>Egg groups</b>: {egg_groups}
<b>Egg cycles</b>: {egg_cycles}

<b><u>Base stats</u></b>
{stats}
'''

SHINY_PAGE = f'''
<b><u>{SHINY_PAGE_TITLE}</u></b> <a href='{SHINY_PAGE_THUMB_URL}'>\
{TYPE_EMOJI['bird']}</a> {TYPE_EMOJI['normal']}

<b><u>Evolutions</u></b>
<i>This Pokémon does not even exist</i>

<b><u>Base stats</u></b>
33 HP {BLACK_CIRCLE * 2}
136 ATK {BLACK_CIRCLE * 6}
0 DEF {BLACK_CIRCLE * 10}
6 SPCL {BLACK_CIRCLE * 1}
29 SPE {BLACK_CIRCLE * 2}
'''

ABILITY_PAGE = '''
{ability_emoji} <b><u>{name}</u></b>
<i>Introduced in {generation}</i>

{description_emoji} <b><u>Description</u></b>
{description}

{pokemon_list_emoji} <b><u>List of Pokémon</u></b>
{pokemon_list}
'''

MOVE_PAGE = '''
{move_emoji} <b><u>{name}</u></b>
<i>Introduced in {generation}</i>

{data_emoji} <b><u>Data</u></b>
<b>Type</b>: {type} {type_emoji}
<b>Category</b>: {class}
<b>Power</b>: {power} | <b>Accuracy</b>: {accuracy} | <b>PP</b>: {pp}

{description_emoji} <b><u>Description</u></b>
{description}
'''