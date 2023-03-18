import json
import re
import uvloop

from pokepy import V2Client as pokemon_client
from pyrogram import Client, filters

import data
import inline
import datapage
import moves
import markup
import shiny
import const


uvloop.install()
app = Client(const.SESSION_NAME,
    api_id=const.API_ID,
    api_hash=const.API_HASH,
    bot_token=const.BOT_TOKEN
)
with open(const.USER_SETTINGS_PATH) as f:
    user_settings = json.load(f)
user_query_results = {}


@app.on_message(filters.command('start'))
async def start(client, message):
    '''/start command:
    it shows a brief description of the bot and the usage'''

    user_id = message.from_user.id
    if str(user_id) not in user_settings:
        create_user_settings(user_id)

    is_preview_hidden = False
    reply_markup = None

    if len(message.command) == 1:
        # Regular /start
        if is_shiny_unlocked(user_id):
            text = const.START_SHINY_UNLOCKED
        else:
            text = const.START
    else:
        # Link to data (e.g.: ability, move, another Pokémon) page
        key, value = message.command[1].split('-', maxsplit=1)

        if key == 'pokemon':
            is_expanded = False
            pokemon = pokemon_client().get_pokemon(value).pop()
            text = datapage.get_datapage_text(pokemon, is_expanded, is_shiny_setted(user_id))
            reply_markup = markup.datapage_markup(pokemon.name)

        if key == 'ability':
            is_preview_hidden = True
            ability = pokemon_client().get_ability(value).pop()
            text = data.get_ability_page_text(ability)

        if key == 'move':
            is_preview_hidden = True
            move = pokemon_client().get_move(value).pop()
            text = moves.get_move_page_text(move)

    await client.send_message(
        chat_id=user_id,
        text=text,
        reply_markup=reply_markup,
        disable_web_page_preview=is_preview_hidden
    )


@app.on_message(filters.command('toggle_shiny'))
async def toggle_shiny(client, message):
    '''set/unset the Pokémon shiny form for the thumbnail'''

    user_id = message.from_user.id
    if str(user_id) not in user_settings:
        create_user_settings(user_id)

    if is_shiny_unlocked(user_id):
        if is_shiny_setted(user_id):
            unset_shiny(user_id)
            text = const.UNSET_SHINY
        else:
            set_shiny(user_id)
            text = const.SET_SHINY

        await client.send_message(
            chat_id=user_id,
            text=text
        )


@app.on_inline_query()
async def inline_search(client, inline_query):
    '''Search Pokémon via inline mode.
    It shows one or more query results based on the input.
    e.g.:
    @rotogrambot rotom'''

    user_id = inline_query.from_user.id
    query_message = inline_query.query
    if str(user_id) not in user_settings:
        create_user_settings(user_id)

    if not inline.has_minimum_characters(query_message):
        await inline.show_help_button(inline_query)
        return

    match_list = inline.get_matching_pokemon(query_message.lower())
    query_results = inline.get_query_results(match_list, is_shiny_setted(user_id))
    store_user_query_results(query_results, match_list, user_id)

    await inline_query.answer(
        results=query_results,
        cache_time=const.CACHE_TIME
    )


@app.on_chosen_inline_result()
async def create_page(client, inline_query):
    '''Create page of chosen Pokémon'''

    user_id = inline_query.from_user.id
    result_id = inline_query.result_id
    message_id = inline_query.inline_message_id
    pokemon_name = user_query_results[user_id][result_id]
    if str(user_id) not in user_settings:
        create_user_settings(user_id)

    if shiny.is_shiny_keyword(pokemon_name):
        await shiny.load_shiny_page(app, inline_query, is_shiny_unlocked(user_id))
        return

    pokemon = pokemon_client().get_pokemon(pokemon_name).pop()
    is_expanded = False

    await client.edit_inline_text(
        inline_message_id=message_id,
        text=datapage.get_datapage_text(pokemon, is_expanded, is_shiny_setted(user_id)),
        reply_markup=markup.datapage_markup(pokemon_name)
    )


@app.on_callback_query(filters.create(lambda _, __, query: 'infos' in query.data))
async def expand(client, query):
    '''Expand/Reduce button:
    get more/less data (such as Pokédex and other game data)'''

    user_id = query.from_user.id
    message_id = query.inline_message_id
    if str(user_id) not in user_settings:
        create_user_settings(user_id)

    # first value (underscore) is useless, it's just used to call expand()
    _, is_expanded, pokemon_name = re.split('/', query.data)
    is_expanded = int(is_expanded)

    pokemon = pokemon_client().get_pokemon(pokemon_name).pop()

    # Page is created by a link
    if message_id is None:
        return await query.message.edit_text(
            text=datapage.get_datapage_text(pokemon, is_expanded, is_shiny_setted(user_id)),
            reply_markup=markup.datapage_markup(pokemon_name, is_expanded)
        )

    await client.answer_callback_query(query.id)  # Delete the loading circle
    await client.edit_inline_text(
        inline_message_id=message_id,
        text=datapage.get_datapage_text(pokemon, is_expanded, is_shiny_setted(user_id)),
        reply_markup=markup.datapage_markup(pokemon_name, is_expanded)
    )


@app.on_callback_query(filters.create(lambda _, __, query: 'movepool' in query.data))
async def show_movepool(client, query):
    '''Movepool button:
    show all moves and their main parameters that a Pokémon can learn'''

    user_id = query.from_user.id
    message_id = query.inline_message_id
    if str(user_id) not in user_settings:
        create_user_settings(user_id)

    # first value (underscore) is useless, it's just used to call get_movepool()
    _, current_page, pokemon_name = re.split('/', query.data)
    current_page = int(current_page)

    pokemon = pokemon_client().get_pokemon(pokemon_name).pop()

    # Page is created by a link
    if message_id is None:
        return await query.message.edit_text(
            text=moves.get_movepool_page(pokemon, current_page, is_shiny_setted(user_id)),
            reply_markup=markup.movepool_markup(pokemon, current_page)
        )

    await client.answer_callback_query(query.id)  # Delete the loading circle
    await client.edit_inline_text(
        inline_message_id=message_id,
        text=moves.get_movepool_page(pokemon, current_page, is_shiny_setted(user_id)),
        reply_markup=markup.movepool_markup(pokemon, current_page)
    )


@app.on_callback_query(filters.create(lambda _, __, query: 'shiny_prompt' == query.data))
async def show_shiny_page(client, query):
    '''Show the hidden page for unlock shiny thumbnails'''

    user_id = query.from_user.id
    message_id = query.inline_message_id
    if str(user_id) not in user_settings:
        create_user_settings(user_id)

    await client.answer_callback_query(query.id)  # Delete the loading circle
    await client.edit_inline_text(
        inline_message_id=message_id,
        text='???',
        reply_markup=markup.accept_shiny()
    )


@app.on_callback_query(filters.create(lambda _, __, query: 'accept_shiny' == query.data))
async def accept_shiny(client, query):
    '''Unlock shiny thumbnails'''

    user_id = query.from_user.id
    message_id = query.inline_message_id
    if str(user_id) not in user_settings:
        create_user_settings(user_id)

    unlock_shiny(user_id)

    await client.edit_inline_text(
        inline_message_id=message_id,
        text=const.SHINY_ACCEPTED
    )


def store_user_query_results(query_results, match_list, user_id):
    user_query_results[user_id] = {}
    for result, pokemon_name in zip(query_results, match_list):
        user_query_results[user_id] |= {result.id: pokemon_name}


def create_user_settings(user_id):
    # user_id is stored as string because json.dump() would generate
    # duplicate if we use int, since it would eventually converted in a string
    user_settings[str(user_id)] = {
        'shiny': False,
        'is_shiny_unlocked': False
    }
    dump_user_settings()


def is_shiny_setted(user_id):
    return user_settings[str(user_id)]['shiny'] is True


def set_shiny(user_id):
    user_settings[str(user_id)]['shiny'] = True
    dump_user_settings()


def unset_shiny(user_id):
    user_settings[str(user_id)]['shiny'] = False
    dump_user_settings()


def is_shiny_unlocked(user_id):
    return user_settings[str(user_id)]['is_shiny_unlocked'] is True


def unlock_shiny(user_id):
    user_settings[str(user_id)]['is_shiny_unlocked'] = True
    dump_user_settings()


def dump_user_settings():
    with open(const.USER_SETTINGS_PATH, 'w') as f:
        json.dump(user_settings, f, indent=4)


if __name__ == '__main__':
    app.run()
