import re
import uvloop

from pokepy import V2Client as pokemon_client
from pyrogram import Client, filters

import inline
import datapage
import movepool
import markup
import shiny
import script
import const


uvloop.install()
client = Client(const.SESSION_NAME)
user_settings = {}
user_query_results = {}


@client.on_message(filters.command('start'))
async def start(Client, message):
    '''/start command:
    it shows a brief description of the bot and the usage'''

    user_id = message.from_user.id
    if user_id not in user_settings:
        create_user_settings(user_id)

    if is_shiny_unlocked(user_id):
        text = script.start_shiny_unlocked
    else:
        text = script.start

    await Client.send_message(
        chat_id=user_id,
        text=text
    )


@client.on_message(filters.command('toggle_shiny'))
async def toggle_shiny(Client, message):
    '''set/unset the Pokémon shiny form for the thumbnail'''

    user_id = message.from_user.id
    if user_id not in user_settings:
        create_user_settings(user_id)

    if is_shiny_unlocked(user_id):
        if is_shiny_setted(user_id):
            unset_shiny(user_id)
            text = script.unset_shiny
        else:
            set_shiny(user_id)
            text = script.set_shiny

        await Client.send_message(
            chat_id=user_id,
            text=text
        )


@client.on_inline_query()
async def inline_search(Client, inline_query):
    '''Search Pokémon via inline mode.
    It shows one or more query results based on the input.
    e.g.:
    @rotogrambot rotom'''

    user_id = inline_query.from_user.id
    query_message = inline_query.query
    if user_id not in user_settings:
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


@client.on_chosen_inline_result()
async def create_page(app, inline_query):
    '''Create page of chosen Pokémon'''

    user_id = inline_query.from_user.id
    result_id = inline_query.result_id
    message_id = inline_query.inline_message_id
    pokemon_name = user_query_results[user_id][result_id]
    if user_id not in user_settings:
        create_user_settings(user_id)

    if shiny.is_shiny_keyword(pokemon_name):
        await shiny.load_shiny_page(app, inline_query, is_shiny_unlocked(user_id))
        return

    pokemon = pokemon_client().get_pokemon(pokemon_name).pop()

    await app.edit_inline_text(
        inline_message_id=message_id,
        text=datapage.get_datapage_text(pokemon, is_shiny_setted(user_id)),
        reply_markup=markup.datapage_markup(pokemon_name)
    )


@client.on_callback_query(filters.create(lambda _, __, query: 'infos' in query.data))
async def expand(app, query):
    '''Expand/Reduce button:
    get more/less data (such as Pokédex and other game data)'''

    user_id = query.from_user.id
    message_id = query.inline_message_id
    if user_id not in user_settings:
        create_user_settings(user_id)

    # first value (underscore) is useless, it's just used to call expand()
    _, is_expanded, pokemon_name = re.split('/', query.data)
    is_expanded = int(is_expanded)

    pokemon = pokemon_client().get_pokemon(pokemon_name).pop()

    await app.answer_callback_query(query.id)  # Delete the loading circle
    await app.edit_inline_text(
        inline_message_id=message_id,
        text=datapage.get_datapage_text(pokemon, is_expanded, is_shiny_setted(user_id)),
        reply_markup=markup.datapage_markup(pokemon_name, is_expanded)
    )


@client.on_callback_query(filters.create(lambda _, __, query: 'movepool' in query.data))
async def show_movepool(app, query):
    '''Movepool button:
    show all moves and their main parameters that a Pokémon can learn'''

    user_id = query.from_user.id
    message_id = query.inline_message_id
    if user_id not in user_settings:
        create_user_settings(user_id)

    # first value (underscore) is useless, it's just used to call get_movepool()
    _, current_page, pokemon_name = re.split('/', query.data)
    current_page = int(current_page)

    pokemon = pokemon_client().get_pokemon(pokemon_name).pop()

    await app.answer_callback_query(query.id)  # Delete the loading circle
    await app.edit_inline_text(
        inline_message_id=message_id,
        text=movepool.get_movepool_page(pokemon, current_page, is_shiny_setted(user_id)),
        reply_markup=markup.movepool_markup(pokemon, current_page)
    )


@client.on_callback_query(filters.create(lambda _, __, query: 'shiny_prompt' == query.data))
async def show_shiny_page(app, query):
    '''Show the hidden page for unlock shiny thumbnails'''

    user_id = query.from_user.id
    message_id = query.inline_message_id
    if user_id not in user_settings:
        create_user_settings(user_id)

    await app.answer_callback_query(query.id)  # Delete the loading circle
    await app.edit_inline_text(
        inline_message_id=message_id,
        text='???',
        reply_markup=markup.accept_shiny()
    )


@client.on_callback_query(filters.create(lambda _, __, query: 'accept_shiny' == query.data))
async def accept_shiny(app, query):
    '''Unlock shiny thumbnails'''

    user_id = query.from_user.id
    message_id = query.inline_message_id
    if user_id not in user_settings:
        create_user_settings(user_id)

    unlock_shiny(user_id)

    await app.edit_inline_text(
        inline_message_id=message_id,
        text=script.shiny_accepted
    )


def store_user_query_results(query_results, match_list, user_id):
    user_query_results[user_id] = {}
    for result, pokemon_name in zip(query_results, match_list):
        user_query_results[user_id] |= {result.id: pokemon_name}


def create_user_settings(user_id):
    user_settings[user_id] = {
        'shiny': False,
        'is_shiny_unlocked': False
    }


def is_shiny_setted(user_id):
    return user_settings[user_id]['shiny'] is True


def set_shiny(user_id):
    user_settings[user_id]['shiny'] = True


def unset_shiny(user_id):
    user_settings[user_id]['shiny'] = False


def is_shiny_unlocked(user_id):
    return user_settings[user_id]['is_shiny_unlocked'] is True


def unlock_shiny(user_id):
    user_settings[user_id]['is_shiny_unlocked'] = True


if __name__ == '__main__':
    client.run()
