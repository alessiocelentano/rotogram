import re

from pyrogram import filters

from client import client, pokemon_client
from inline_search import (has_minimum_characters, show_help_button,
                           get_matching_pokemon, create_inline_query_results)
from create_page import create_datapage_text, create_datapage_markup
import script
import const


user_query_dict = dict()


@client.on_message(filters.command('start'))
async def start(client, message):
    await client.send_message(
        chat_id=message.from_user.id,
        text=script.start
    )


@client.on_inline_query()
async def inline_search(client, inline_query):
    if not has_minimum_characters(inline_query.query):
        await show_help_button(inline_query)
        return
    match_list = get_matching_pokemon(inline_query.query.lower())
    results = create_inline_query_results(match_list)
    store_user_current_results(results, match_list, inline_query.from_user.id)
    await inline_query.answer(
        results=results,
        cache_time=const.CACHE_TIME
    )


@client.on_chosen_inline_result()
async def create_page(app, inline_query):
    species_name = user_query_dict[inline_query.from_user.id][inline_query.result_id]
    species = pokemon_client.get_pokemon_species(species_name).pop()
    text = create_datapage_text(species, is_expanded=False)
    markup = create_datapage_markup(species.name, is_expanded=False)
    await app.edit_inline_text(
        inline_message_id=inline_query.inline_message_id,
        text=text,
        reply_markup=markup
    )


@client.on_callback_query(filters.create(lambda _, __, query: 'infos' in query.data))
async def expand(app, query):
    # first value (underscore) is useless, it's just used to call expand()
    _, is_expanded, species_name = re.split('/', query.data)
    is_expanded = int(is_expanded)
    species = pokemon_client.get_pokemon_species(species_name).pop()
    text = create_datapage_text(species, is_expanded=is_expanded)
    markup = create_datapage_markup(species.name, is_expanded=is_expanded)
    await app.answer_callback_query(query.id)  # Delete the loading circle
    await app.edit_inline_text(
        inline_message_id=query.inline_message_id,
        text=text,
        reply_markup=markup
    )


def store_user_current_results(results, match_list, user_id):
    user_query_dict[user_id] = {r.id: species_name for r, species_name in zip(results, match_list)}


if __name__ == '__main__':
    client.run()
