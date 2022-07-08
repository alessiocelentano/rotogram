import const


start = f'''
{const.ZAP} <b><u>What is Rotogram?</u></b>
Rotogram is a bot which acts as a helper for trainers on Telegram. \
You can check information of Pokemon, Showdown usage and more \
as quickly as possible, without ever leaving Telegram\n
{const.TOOL} <b><u>Usage</u></b>
Just write Pokemon name after @rotogrambot (e.g.: @rotogrambot Rotom)\n
@alessiocelentano | \
<a href='t.me/rotogram'>Follow us</a> | \
<a href='github.com/alessiocelentano/rotogram'>GitHub</a>
'''
shiny_accepted = f'''
You accepted a strange gift.
It contains a message:

"<i>Yo trainer, try to search some Pokémon on Rotogram with this new item.
It contains two commands: /set_shiny and /unset_shiny.
By default is setted on. Follow me on @rotogram for more news like this.

with {const.HEART} ,
- the developer</i>"
'''

loading = f'{const.LOADING_CIRCLE}  Loading...'
shiny_page_loading = f'{const.GLYPH_NOT_FOUND} L?ad?ng...?'
reduce = f'{const.MINUS}  Reduce'
expand = f'{const.PLUS}  Expand'
movepool = f'{const.SWORDS}  Moves'
location = f'{const.HOUSE}  Locations'
back = f'{const.BACK} Back'
accept_shiny_button = f'{const.TICK} ACCEPT GIFT'
set_shiny_command = 'Shiny images setted successfully!'
unset_shiny_command = 'Shiny images unsetted successfully!'
no_evolutions = '<i>It is not known to evolve into or from any other Pokémon</i>\n'

shedinja_method = '''\
evolve Nincada having one Poké Ball in bag and one empty slot in party
'''
malamar_method = '''\
while the game system is held upside-down
'''
sirfetch_method = '''\
land three critical hits in one battle
'''
runerigus_method = '''\
travel under the stone bridge in Dusty Bowl after taking at least \
49 damage from attacks without fainting
'''
alcremie_method = '''\
while holding a Sweet when its Trainer spins and strikes a pose
'''
urshifu_method = '''\
interact with Scroll of Darkness/Waters
'''


def pokemon_page(data, is_expanded=False):
    # Just check one variable. If that line is not empty, expand_data has to be prompted
    expand_text = get_expand_data(data) if is_expanded else ''
    type_title = 'Types' if '/' in data['types'] else 'Type'
    ability_title = 'Abilities' if '/' in data['abilities'] else 'Ability'
    hidden_ability_line = f'\n<b>Hidden Ability</b>: {data["hidden_ability"]}' if data['hidden_ability'] else ''
    return f'''
<b><u>{data['name']}</u></b> <a href='{data['artwork_link']}'> \
{const.TYPE_EMOJI[data['primary_type']]}</a> {const.TYPE_EMOJI[data['secondary_type']]}
<b>{type_title}</b>: {data["types"]}
<b>{ability_title}</b>: {data['abilities']} \
{hidden_ability_line}\n
<b><u>Evolutions</u></b>
{data['evolution_family']} \
{expand_text}
<b><u>Base stats</u></b>
{data['stats']['hp']} HP {data['stats_rating']['hp']}
{data['stats']['attack']} ATK {data['stats_rating']['attack']}
{data['stats']['defense']} DEF {data['stats_rating']['defense']}
{data['stats']['special-attack']} SPA {data['stats_rating']['special-attack']}
{data['stats']['special-defense']} SPD {data['stats_rating']['special-defense']}
{data['stats']['speed']} SPE {data['stats_rating']['speed']}
'''


def get_expand_data(data):
    return f'''
<u><b>Pokédex data</b></u>
<b>Species</b>: {data["genus"]}
<b>National Pokedex Number</b>: {data["dex_number"]}
<b>Height</b>: {data["height"]}
<b>Weight</b>: {data["weight"]}
<b>Gender (male/female)</b>: {data["gender_percentage"]}\n
<u><b>Game data</b></u>
<b>Base friendship</b>: {data["base_friendship"]}
<b>EV yield</b>: {data["ev_yield_text"]}
<b>Catch rate</b>: {data["catch_rate"]}
<b>Growth rate</b>: {data["growth_rate"]}
<b>Egg groups</b>: {data["egg_groups_text"]}
<b>Egg cycles</b>: {data["egg_cycles"]}
'''


shiny_page = f'''
<b><u>{const.SHINY_PAGE_TITLE}</u></b> <a href='{const.SHINY_PAGE_THUMB_URL}'> \
{const.TYPE_EMOJI["bird"]}</a> {const.TYPE_EMOJI["normal"]} \n
<b><u>Evolutions</u></b>
<i>This Pokémon does not even exist</i>\n
<b><u>Base stats</u></b>
33 HP {const.BLACK_CIRCLE * 2}
136 ATK {const.BLACK_CIRCLE * 6}
0 DEF {const.BLACK_CIRCLE * 10}
6 SPCL {const.BLACK_CIRCLE * 1}
29 SPE {const.BLACK_CIRCLE * 2}
'''


def add_movepool_title(current_page, total_pages, artwork):
    return f' <a href=\'{artwork}\'>{const.RED_SPARK}</a> <u><b>Movepool ({current_page}/{total_pages})</b></u>\n'


def add_movepool_line(name, class_, type_, power, accuracy):
    return f'''
– <b>{name}</b> – (<i>{class_}</i>)
<b>Type</b>: {type_} {const.TYPE_EMOJI[type_.lower()]}
<b>Power</b>: {power} | <b>Accuracy</b>: {accuracy}
'''
