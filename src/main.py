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
with open(const.CHATS_PATH) as f:
    chats = json.load(f)
user_query_results = {}


@app.on_message(filters.create(lambda _, __, message: str(message.chat.id) not in chats), group=-1)
async def new_chat(client, message):
    chat_id = message.chat.id
    chat_type =  message.chat.type.value
    chat_name = message.chat.title if message.chat.title else message.chat.first_name
    chat_username = message.chat.username
    add_chat(chat_id, chat_type, chat_name, chat_username)


@app.on_inline_query(group=-1)
async def new_chat(client, query):
    chat_id = query.from_user.id
    chat_type = 'private'
    chat_name = query.from_user.first_name
    chat_username = query.from_user.username
    add_chat(chat_id, chat_type, chat_name, chat_username)


@app.on_message(filters.command('start', prefixes=['.', '/', '!']))
async def start(client, message):
    '''/start command:
    it shows a brief description of the bot and the usage'''

    chat_id = message.chat.id
    user_id = message.from_user.id
    is_preview_hidden = False
    reply_markup = None

    if len(message.command) == 1 or message.command[1] == 'start':
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
            text = datapage.get_datapage_text(pokemon, get_thumb_type(user_id), is_expanded, is_shiny_setted(user_id))
            reply_markup = markup.datapage_markup(pokemon.name)

        elif key == 'ability':
            is_preview_hidden = True
            ability = pokemon_client().get_ability(value).pop()
            text = data.get_ability_page_text(ability, 1)

        elif key == 'move':
            is_preview_hidden = True
            move = pokemon_client().get_move(value).pop()
            text, pokemon_list = moves.get_move_page_text(move, 1)
            reply_markup = markup.move_markup(value, len(pokemon_list), 1)

    await client.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=reply_markup,
        disable_web_page_preview=is_preview_hidden
    )


@app.on_message(filters.regex('[\.\/\!]move [a-zA-Z\-]+\s*\?\s*[a-zA-Z\-]+'))
async def move_mon(client, message):
    user_id = message.chat.id

    move_name = message.text.split()[1][:-1].lower()
    pokemon_name = message.text.split()[2].lower()
    move = pokemon_client().get_move(move_name).pop()
    pokemon = pokemon_client().get_pokemon(pokemon_name).pop()
    species = pokemon_client().get_pokemon_species(pokemon.species.name).pop()

    for m in pokemon.moves:
        if m.move.name == move.name:
            text = const.POKEMON_LEARN_MOVE.format(const.TICK, data.get_pokemon_full_name(pokemon, species), data.get_english_name(move.names), '')
            break
    else:
        text = const.POKEMON_DOESNT_LEARN_MOVE.format(const.X, data.get_pokemon_full_name(pokemon, species), data.get_english_name(move.names), '')

    await client.send_message(
        chat_id=user_id,
        text=text,
        disable_web_page_preview=True
    )


@app.on_message(filters.command('move', prefixes=['.', '/', '!']))
async def move(client, message):
    user_id = message.chat.id

    move_name = message.command[1].lower()
    move = pokemon_client().get_move(move_name).pop()

    text, pokemon_list = moves.get_move_page_text(move, 1)
    reply_markup = markup.move_markup(move_name, len(pokemon_list), 1)

    await client.send_message(
        chat_id=user_id,
        text=text,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )


@app.on_callback_query(filters.create(lambda _, __, query: 'who_learn_move' in query.data))
async def scroll_move_pokemon_list(client, query):
    user_id = query.from_user.id
    message_id = query.inline_message_id

    _, current_page, move_name = re.split('/', query.data)
    current_page = int(current_page)

    move = pokemon_client().get_move(move_name).pop()
    text, pokemon_list = moves.get_move_page_text(move, current_page)
    reply_markup = markup.move_markup(move_name, len(pokemon_list), current_page)

    return await query.message.edit_text(
        text=text,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )


@app.on_message(filters.command('pics', prefixes=['.', '/', '!']))
async def pics(client, message):
    '''Choose new Pokemon pictures'''

    chat_id = message.chat.id
    user_id = message.from_user.id
    thumb_type = chats[str(user_id)]['thumb_type']

    await client.send_message(
        chat_id=chat_id,
        text=const.PICS,
        reply_markup=markup.pics_markup(thumb_type)
    )


@app.on_callback_query(filters.create(lambda _, __, query: query.data in ['official artwork', 'home', 'showdown']))
async def change_pics(client, query):
    '''Change Pokémon pictures'''

    user_id = query.from_user.id
    message = query.message

    set_thumb_type(user_id, query.data)

    await message.edit_text(text=const.PICS_CHANGED)


@app.on_message(filters.command('shiny', prefixes=['.', '/', '!']))
async def toggle_shiny(client, message):
    '''Set/Unset the Pokémon shiny form for the thumbnail'''

    chat_id = message.chat.id
    user_id = message.from_user.id

    if is_shiny_unlocked(user_id):
        if is_shiny_setted(user_id):
            unset_shiny(user_id)
            text = const.UNSET_SHINY
        else:
            set_shiny(user_id)
            text = const.SET_SHINY

        await client.send_message(
            chat_id=chat_id,
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

    if not inline.has_minimum_characters(query_message):
        await inline.show_help_button(inline_query)
        return

    match_list = inline.get_matching_pokemon(query_message.lower())
    query_results = inline.get_query_results(match_list, get_thumb_type(user_id), is_shiny_setted(user_id))
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

    if shiny.is_shiny_keyword(pokemon_name):
        await shiny.load_shiny_page(app, inline_query, is_shiny_unlocked(user_id))
        return

    pokemon = pokemon_client().get_pokemon(pokemon_name).pop()
    is_expanded = False

    await client.edit_inline_text(
        inline_message_id=message_id,
        text=datapage.get_datapage_text(pokemon, get_thumb_type(user_id), is_expanded, is_shiny_setted(user_id)),
        reply_markup=markup.datapage_markup(pokemon_name)
    )


@app.on_callback_query(filters.create(lambda _, __, query: 'infos' in query.data))
async def expand(client, query):
    '''Expand/Reduce button:
    get more/less data (such as Pokédex and other game data)'''

    user_id = query.from_user.id
    message_id = query.inline_message_id

    # first value (underscore) is useless, it's just used to call expand()
    _, is_expanded, pokemon_name = re.split('/', query.data)
    is_expanded = int(is_expanded)

    pokemon = pokemon_client().get_pokemon(pokemon_name).pop()

    # Page is created by a link
    if message_id is None:
        return await query.message.edit_text(
            text=datapage.get_datapage_text(pokemon, get_thumb_type(user_id), is_expanded, is_shiny_setted(user_id)),
            reply_markup=markup.datapage_markup(pokemon_name, is_expanded)
        )

    await client.answer_callback_query(query.id)  # Delete the loading circle
    await client.edit_inline_text(
        inline_message_id=message_id,
        text=datapage.get_datapage_text(pokemon, get_thumb_type(user_id), is_expanded, is_shiny_setted(user_id)),
        reply_markup=markup.datapage_markup(pokemon_name, is_expanded)
    )


@app.on_callback_query(filters.create(lambda _, __, query: 'movepool' in query.data))
async def show_movepool(client, query):
    '''Movepool button:
    show all moves and their main parameters that a Pokémon can learn'''

    user_id = query.from_user.id
    message_id = query.inline_message_id

    # first value (underscore) is useless, it's just used to call get_movepool()
    _, current_page, pokemon_name = re.split('/', query.data)
    current_page = int(current_page)

    pokemon = pokemon_client().get_pokemon(pokemon_name).pop()

    # Page is created by a link
    if message_id is None:
        return await query.message.edit_text(
            text=moves.get_movepool_page(pokemon, current_page, get_thumb_type(user_id), is_shiny_setted(user_id)),
            reply_markup=markup.movepool_markup(len(pokemon.moves), pokemon.name, current_page)
        )

    await client.answer_callback_query(query.id)  # Delete the loading circle
    await client.edit_inline_text(
        inline_message_id=message_id,
        text=moves.get_movepool_page(pokemon, current_page, get_thumb_type(user_id), is_shiny_setted(user_id)),
        reply_markup=markup.movepool_markup(len(pokemon.moves), pokemon.name, current_page)
    )


@app.on_callback_query(filters.create(lambda _, __, query: 'shiny_prompt' == query.data))
async def show_shiny_page(client, query):
    '''Show the hidden page for unlock shiny thumbnails'''

    user_id = query.from_user.id
    message_id = query.inline_message_id

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

    unlock_shiny(user_id)

    await client.edit_inline_text(
        inline_message_id=message_id,
        text=const.SHINY_ACCEPTED
    )


@app.on_message(filters.private & filters.create(lambda _, __, message: message.from_user.id != int(const.OWNER)), group=1)
async def forward_to_owner(client, message):
    '''Forward private message to the owner'''

    name = message.from_user.first_name
    username = message.from_user.username
    user_id = message.from_user.id
    
    await client.send_message(
        chat_id=const.OWNER,
        text=const.FORWARD_MESSAGE_NOTIFICATION.format(const.MESSAGE, name, username, user_id),
    )
    await message.forward(const.OWNER)


@app.on_message(filters.private & filters.command('reply', prefixes=['.', '/', '!']) & filters.create(lambda _, __, message: message.from_user.id == int(const.OWNER)), group=1)
async def owner_reply(client, message):
    '''Reply to users'''

    user_id = message.command[1]
    text = ' '.join(message.command[2:])

    await client.send_message(
        chat_id=user_id,
        text=text
    )


@app.on_message(filters.command('broadcast', prefixes=['.', '/', '!']) & filters.private & filters.create(lambda _, __, message: message.from_user.id == int(const.OWNER)), group=1)
async def broadcast_message(client, message):
    '''Broadcast a message to all saved chats'''
    text = ' '.join(message.command[1:])

    for user_id in chats:
        try:
            await client.send_message(
                chat_id=int(user_id),
                text=text
            )
        except Exception:
            pass


@app.on_message(filters.command('mon', prefixes=['.', '/', '!']) | filters.regex('[\.\/\!].+'))
async def command_search(client, message):
    '''Search Pokémon via command.
    e.g.: !rotom
    '''
    user_id = message.from_user.id
    chat_id = message.chat.id

    try:
        pokemon_name = message.text[5:].lower() if re.match('[\.\/\!]mon', message.text[:4]) else message.text[1:].lower()
        pokemon = pokemon_client().get_pokemon(pokemon_name).pop()
    except Exception:
        return

    is_expanded = False
    await client.send_message(
        chat_id=chat_id,
        text=datapage.get_datapage_text(pokemon, get_thumb_type(user_id), is_expanded, is_shiny_setted(chat_id)),
        reply_markup=markup.datapage_markup(pokemon_name)
    )


def store_user_query_results(query_results, match_list, user_id):
    user_query_results[user_id] = {}
    for result, pokemon_name in zip(query_results, match_list):
        user_query_results[user_id] |= {result.id: pokemon_name}


def add_chat(chat_id, chat_type, chat_name, chat_username):
    # user_id is stored as string because json.dump() would generate
    # duplicate if we use int, since it would eventually converted in a string
    chats[str(chat_id)] = {
        'type': chat_type,
        'name': chat_name,
        'username': chat_username,
        'thumb_type': 'home',
        'shiny': False,
        'is_shiny_unlocked': False
    }
    dump_chats()


def set_thumb_type(user_id, thumb_type):
    chats[str(user_id)]['thumb_type'] = thumb_type
    dump_chats()


def get_thumb_type(user_id):
    return chats[str(user_id)]['thumb_type']


def is_shiny_setted(user_id):
    return chats[str(user_id)]['shiny'] is True if str(user_id) in chats else False


def set_shiny(user_id):
    chats[str(user_id)]['shiny'] = True
    dump_chats()


def unset_shiny(user_id):
    chats[str(user_id)]['shiny'] = False
    dump_chats()


def is_shiny_unlocked(user_id):
    return chats[str(user_id)]['is_shiny_unlocked'] is True


def unlock_shiny(user_id):
    chats[str(user_id)]['is_shiny_unlocked'] = True
    dump_chats()


def dump_chats():
    with open(const.CHATS_PATH, 'w') as f:
        json.dump(chats, f, indent=4)


if __name__ == '__main__':
    app.run()
