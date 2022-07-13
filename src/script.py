import const


start = f'''
{const.ZAP} <b><u>What is Rotogram?</u></b>
Rotogram is your detailed and always up-to-date Pokémon bot. \
You can check infos about every specie \
as quickly as possible, without ever leaving Telegram

{const.TOOL} <b><u>Usage</u></b>
Just write Pokemon name after @rotogrambot (e.g.: @rotogrambot Rotom)

@alessiocelentano | \
<a href='t.me/rotogram'>Follow us</a> | \
<a href='github.com/alessiocelentano/rotogram'>GitHub</a>
'''
start_shiny_unlocked = f'''
{const.ZAP} <b><u>What is Rotogram?</u></b>
Rotogram is your detailed and always up-to-date Pokémon bot. \
You can check infos about every specie \
as quickly as possible, without ever leaving Telegram

{const.TOOL} <b><u>Usage</u></b>
Just write Pokemon name after @rotogrambot (e.g.: @rotogrambot Rotom)

{const.SPACE_INVADER} <b>...?</b>
You have a strange item... it has one command:
/toggle_shiny

@alessiocelentano | \
<a href='t.me/rotogram'>Follow us</a> | \
<a href='github.com/alessiocelentano/rotogram'>GitHub</a>
'''
shiny_accepted = f'''
You accepted a strange gift.
It contains a message:

'<i>Yo trainer, try to search some Pokémon on Rotogram with this new item.
It contains a command called /toggle_shiny. Use it on @rotogrambot chat.
Follow me on @rotogram for more news like this.

with {const.HEART} ,
- the developer</i>'
'''

loading = f'{const.LOADING_CIRCLE}  Loading...'
shiny_page_loading = f'{const.GLYPH_NOT_FOUND} L?ad?ng...?'
set_shiny = f'Shiny thumbnails enabled successfully! {const.SHINE}'
unset_shiny = f'Shiny thumbnails disabled {const.X}'
no_evolutions = '<i>It is not known to evolve into or from any other Pokémon</i>'
pokemon_not_found = 'Ooops! Pokémon not found, try again.'
movepool_title = '<a href="{}">{}</a> <u><b>Movepool ({}/{})</b></u>\n'
move = '''
– <b>{name}</b> – (<i>{class}</i>)
<b>Type</b>: {type} {emoji}
<b>Power</b>: {power} | <b>Accuracy</b>: {accuracy}
'''

reduce = f'{const.MINUS}  Reduce'
expand = f'{const.PLUS}  Expand'
movepool = f'{const.SWORDS}  Moves'
location = f'{const.HOUSE}  Locations'
back = f'{const.BACK} Back'
accept_shiny_button = f'{const.TICK} ACCEPT GIFT'

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
travel under the stone bridge in Dusty Bowl after taking at least\
49 damage from attacks without fainting
'''
alcremie_method = '''\
while holding a Sweet when its Trainer spins and strikes a pose
'''
urshifu_method = '''\
interact with Scroll of Darkness/Waters
'''

pokemon_page = '''
<b><u>{pokemon_full_name}</u></b> <a href="{artwork_url}">{emoji1}{emoji2}</a>
<b>{type_section_name}</b>: {typing}
<b>{ability_section_name}</b>: {abilities}\
{hidden_ability_section_name}{hidden_ability}

<b><u>Evolutions</u></b>
{evolution_family}\
{alternative_forms}

<b><u>Base stats</u></b>
{stats}
'''

pokemon_page_expanded = '''
<b><u>{pokemon_full_name}</u></b> <a href="{artwork_url}">{emoji1} {emoji2}</a>
<b>{type_section_name}</b>: {typing}
<b>{ability_section_name}</b>: {abilities}\
{hidden_ability_section_name}{hidden_ability}

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

shiny_page = f'''
<b><u>{const.SHINY_PAGE_TITLE}</u></b> <a href='{const.SHINY_PAGE_THUMB_URL}'>\
{const.TYPE_EMOJI['bird']}</a> {const.TYPE_EMOJI['normal']}

<b><u>Evolutions</u></b>
<i>This Pokémon does not even exist</i>

<b><u>Base stats</u></b>
33 HP {const.BLACK_CIRCLE * 2}
136 ATK {const.BLACK_CIRCLE * 6}
0 DEF {const.BLACK_CIRCLE * 10}
6 SPCL {const.BLACK_CIRCLE * 1}
29 SPE {const.BLACK_CIRCLE * 2}
'''

ability_page = '''
{ability_emoji} <b><u>{name}</u></b>
<i>Introduced in {generation}</i>

{description_emoji} <b><u>Description</u></b>
{description}

{pokemon_list_emoji} <b><u>List of Pokémon</u></b>
{pokemon_list}
'''

move_page = '''
{move_emoji} <b><u>{name}</u></b>
<i>Introduced in {generation}</i>

{data_emoji} <b><u>Data</u></b>
<b>Type</b>: {type} {type_emoji}
<b>Category</b>: {class}
<b>Power</b>: {power} | <b>Accuracy</b>: {accuracy} | <b>PP</b>: {pp}

{description_emoji} <b><u>Description</u></b>
{description}
'''
