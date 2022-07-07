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
loading = f'{const.LOADING_CIRCLE}  Loading...'
reduce = f'{const.MINUS}  Reduce'
expand = f'{const.PLUS}  Expand'
moveset = f'{const.SWORDS}  Moveset'
location = f'{const.HOUSE}  Locations'
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


def pokemon_page(data):
    genus_line = f'<b>Species</b>: {data["genus"]} ' if 'genus' in data else ''
    dex_number_line = f'<b>National Pokedex Number</b>: {data["dex_number"]} ' if 'dex_number' in data else ''
    height_line = f'<b>Height</b>: {data["height"]} ' if 'height' in data else ''
    weight_line = f'<b>Weight</b>: {data["weight"]} ' if 'weight' in data else ''
    gender_line = f'<b>Gender (male/female)</b>: {data["gender_percentage"]} ' if 'gender_percentage' in data else ''
    base_friendship_line = f'<b>Base friendship</b>: {data["base_friendship"]} ' if 'base_friendship' in data else ''
    ev_yield_line = f'<b>EV yield</b>: {data["ev_yield_text"]} ' if 'ev_yield_text' in data else ''
    catch_rate_line = f'<b>Catch rate</b>: {data["catch_rate"]} ' if 'catch_rate' in data else ''
    growth_rate_line = f'<b>Growth rate</b>: {data["growth_rate"]} ' if 'growth_rate' in data else ''
    egg_groups_line = f'<b>Egg groups</b>: {data["egg_groups_text"]} ' if 'egg_groups_text' in data else ''
    egg_cycles_line = f'<b>Egg cycles</b>: {data["egg_cycles"]} ' if 'egg_cycles' in data else ''
    expand_data = ''
    # Just check one variable. If that line is not empty, expand_data has to be prompted
    if genus_line:
        pokedex_data_title = '<u><b>Pokédex data</b></u>'
        game_data_title = '<u><b>Game data</b></u>'
        expand_data = '\n'.join(['', pokedex_data_title, genus_line, dex_number_line,
                                 height_line, weight_line, gender_line, '',
                                 game_data_title, base_friendship_line, ev_yield_line,
                                 catch_rate_line, growth_rate_line, egg_groups_line,
                                 egg_cycles_line, ''])

    type_title = 'Types' if '/' in data['types'] else 'Type'
    ability_title = 'Abilities' if '/' in data['abilities'] else 'Ability'
    hidden_ability_line = f'\n<b>Hidden Ability</b>: {data["hidden_ability"]}' if data['hidden_ability'] else ''

    return f'''
<b><u>{data['name']}</u></b> <a href='{data['artwork_link']}'> \
{const.TYPE_EMOJI[data['primary_type']]}</a> {const.TYPE_EMOJI[data['secondary_type']]}
<b>{type_title}</b>: {data["types"]}
<b>{ability_title}</b>: {data['abilities']} \
{hidden_ability_line}

<b><u>Evolutions</u></b>
{data['evolution_family']} \
{expand_data}
<b><u>Base stats</u></b>
{data['stats']['hp']} HP {data['stats_rating']['hp']}
{data['stats']['attack']} ATK {data['stats_rating']['attack']}
{data['stats']['defense']} DEF {data['stats_rating']['defense']}
{data['stats']['special-attack']} SPA {data['stats_rating']['special-attack']}
{data['stats']['special-defense']} SPD {data['stats_rating']['special-defense']}
{data['stats']['speed']} SPE {data['stats_rating']['speed']}
'''
