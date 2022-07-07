import re

from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent

from client import pokemon_client
from create_page import create_datapage_markup
from misc import (get_english_genus, get_english_name_of,
                  get_default_pokemon_from_species,
                  get_formatted_typing, get_thumb_url)
import script
import const


def has_minimum_characters(message_content):
    return True if len(message_content) > 2 else False


def show_help_button(inline_query):
    return inline_query.answer(
        results=[],
        switch_pm_text='Help',
        switch_pm_parameter='start',
        cache_time=const.CACHE_TIME
    )


def get_matching_pokemon(message_content):
    beginning_list = re.findall(f'^-*{message_content}.*$', const.POKEMON_LIST, flags=re.MULTILINE)
    end_list = re.findall(f'^.*{message_content}-*$', const.POKEMON_LIST, flags=re.MULTILINE)
    any_position_list = re.findall(f'^.*{message_content}.*$', const.POKEMON_LIST, flags=re.MULTILINE)
    return list(dict.fromkeys(beginning_list + end_list + any_position_list))


def create_inline_query_results(match_list):
    results = list()
    for pokemon_name in match_list:
        species = pokemon_client.get_pokemon_species(pokemon_name).pop()
        pokemon = get_default_pokemon_from_species(species)
        name = get_english_name_of(species)
        genus = get_english_genus(species.genera)
        typing = get_formatted_typing(pokemon)
        thumb_url = get_thumb_url(pokemon)
        markup = create_datapage_markup(name)
        results.append(
            InlineQueryResultArticle(
                title=name,
                description=f'{genus}\nType: {typing}',
                input_message_content=InputTextMessageContent(script.loading),
                thumb_url=thumb_url,
                reply_markup=markup
            )
        )
    return results

