import re

from pokepy import V2Client as pokemon_client
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent

import data
import markup
import shiny
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
    if message_content == const.SHINY_KEYWORD:
        return [const.SHINY_KEYWORD]

    beginning_list = re.findall(f'^-*{message_content}.*$', const.POKEMON_LIST, flags=re.MULTILINE)
    end_list = re.findall(f'^.*{message_content}-*$', const.POKEMON_LIST, flags=re.MULTILINE)
    any_position_list = re.findall(f'^.*{message_content}.*$', const.POKEMON_LIST, flags=re.MULTILINE)

    return list(dict.fromkeys(beginning_list + end_list + any_position_list))


def get_query_results(match_list, is_shiny_setted):
    results = []

    for pokemon_name in match_list:
        if pokemon_name == const.SHINY_KEYWORD:
            return shiny.show_shiny_query()

        pokemon = pokemon_client().get_pokemon(pokemon_name).pop()
        species = pokemon_client().get_pokemon_species(pokemon.species.name).pop()

        genus = data.get_english_genus(species.genera)
        typing = data.get_typing(pokemon)

        results.append(
            InlineQueryResultArticle(
                title=data.get_pokemon_full_name(pokemon, species),
                description=f'{genus}\nType: {typing}',
                input_message_content=InputTextMessageContent(script.loading),
                thumb_url=data.get_home_thumb_url(pokemon, is_shiny=is_shiny_setted),
                reply_markup=markup.datapage_markup(pokemon.name, is_expanded=False)
            )
        )

    return results
