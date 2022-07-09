import re

from pyrogram import filters

from client import client, pokemon_client
from inline import (has_minimum_characters, show_help_button,
                    get_matching_pokemon, create_inline_query_results)
import datapage
import movepool
import markup
from shiny import is_shiny_keyword, load_shiny_page
from misc import get_default_pokemon_from_species
import script
import const


user_query_dict = dict()


@client.on_message(filters.command('start'))
async def start(client, message):
    store_user_data(message.from_user.id)
    await client.send_message(
        chat_id=message.from_user.id,
        text=script.start
    )


@client.on_message(filters.command('set_shiny'))
async def set_shiny_command(client, message):
    store_user_data(message.from_user.id)
    if not is_shiny_unlocked(message.from_user.id): return
    set_shiny(message.from_user.id)
    await client.send_message(
        chat_id=message.from_user.id,
        text=script.set_shiny_command
    )


@client.on_message(filters.command('unset_shiny'))
async def unset_shiny_command(client, message):
    store_user_data(message.from_user.id)
    if not is_shiny_unlocked(message.from_user.id): return
    unset_shiny(message.from_user.id)
    await client.send_message(
        chat_id=message.from_user.id,
        text=script.unset_shiny_command
    )


@client.on_inline_query()
async def inline_search(client, inline_query):
    store_user_data(inline_query.from_user.id)

    if not has_minimum_characters(inline_query.query):
        await show_help_button(inline_query)
        return

    match_list = get_matching_pokemon(inline_query.query.lower())
    is_shiny = user_query_dict[inline_query.from_user.id]['shiny']
    results = create_inline_query_results(match_list, is_shiny=is_shiny)

    store_user_current_results(results, match_list, inline_query.from_user.id)
    await inline_query.answer(
        results=results,
        cache_time=const.CACHE_TIME
    )


@client.on_chosen_inline_result()
async def create_page(app, inline_query):
    store_user_data(inline_query.from_user.id)
    species_name = user_query_dict[inline_query.from_user.id][inline_query.result_id]
    is_shiny = user_query_dict[inline_query.from_user.id]['shiny']

    try:
        species = pokemon_client.get_pokemon_species(species_name).pop()
        pokemon = get_default_pokemon_from_species(species)
    except Exception:
        if is_shiny_keyword(species_name):
            await load_shiny_page(app, inline_query, is_shiny_unlocked(inline_query.from_user.id))
        else:
            script.pokemon_not_found()
        return

    await app.edit_inline_text(
        inline_message_id=inline_query.inline_message_id,
        text=datapage.get_text(species, pokemon, is_expanded=False, is_shiny=is_shiny),
        reply_markup=markup.get_datapage(species.name, is_expanded=False)
    )


@client.on_callback_query(filters.create(lambda _, __, query: 'infos' in query.data))
async def expand(app, query):
    store_user_data(query.from_user.id)

    # first value (underscore) is useless, it's just used to call expand()
    _, is_expanded, species_name = re.split('/', query.data)
    is_expanded = int(is_expanded)
    is_shiny = user_query_dict[query.from_user.id]['shiny']

    try:
        species = pokemon_client.get_pokemon_species(species_name).pop()
        pokemon = get_default_pokemon_from_species(species)
    except Exception:
        if is_shiny_keyword(species_name):
            await load_shiny_page(app, query)
            return

    await app.answer_callback_query(query.id)  # Delete the loading circle
    await app.edit_inline_text(
        inline_message_id=query.inline_message_id,
        text=datapage.get_text(species, pokemon, is_expanded=is_expanded, is_shiny=is_shiny),
        reply_markup=markup.get_datapage(species_name, is_expanded=is_expanded)
    )


@client.on_callback_query(filters.create(lambda _, __, query: 'movepool' in query.data))
async def get_movepool(app, query):
    store_user_data(query.from_user.id)

    _, current_page, species_name = re.split('/', query.data)
    current_page = int(current_page)
    species = pokemon_client.get_pokemon_species(species_name).pop()
    pokemon = get_default_pokemon_from_species(species)

    await app.answer_callback_query(query.id)  # Delete the loading circle
    await app.edit_inline_text(
        inline_message_id=query.inline_message_id,
        text=movepool.get_text(pokemon, current_page),
        reply_markup=markup.get_movepool(pokemon, current_page)
    )


@client.on_callback_query(filters.create(lambda _, __, query: 'shiny_prompt' == query.data))
async def get_shiny_page(app, query):
    store_user_data(query.from_user.id)
    await app.answer_callback_query(query.id)  # Delete the loading circle
    await app.edit_inline_text(
        inline_message_id=query.inline_message_id,
        text='???',
        reply_markup=markup.accept_shiny()
    )


@client.on_callback_query(filters.create(lambda _, __, query: 'accept_shiny' == query.data))
async def accept_shiny(app, query):
    store_user_data(query.from_user.id)
    hide_missingno(query.from_user.id)
    set_shiny(query.from_user.id)
    await app.edit_inline_text(
        inline_message_id=query.inline_message_id,
        text=script.shiny_accepted
    )


def store_user_data(user_id):
    if user_id not in user_query_dict:
        user_query_dict[user_id] = {
            'shiny': False,
            'is_missingno_found': False
        }


def store_user_current_results(results, match_list, user_id):
    user_query_dict[user_id] |= {r.id: species_name for r, species_name in zip(results, match_list)}


def is_shiny_setted(user_id):
    return user_query_dict[user_id]['shiny'] is True


def is_shiny_unlocked(user_id):
    return user_query_dict[user_id]['is_missingno_found'] is True


def set_shiny(user_id):
    user_query_dict[user_id]['shiny'] = True


def unset_shiny(user_id):
    user_query_dict[user_id]['shiny'] = False


def hide_missingno(user_id):
    user_query_dict[user_id]['is_missingno_found'] = True


if __name__ == '__main__':
    client.run()
