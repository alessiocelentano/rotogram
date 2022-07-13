from math import ceil

from pokepy import V2Client as pokemon_client

import data
import script
import const


def get_movepool_page(pokemon, current_page, is_shiny_setted):
    total_pages = ceil(len(pokemon.moves) / const.MOVE_PER_PAGE)
    last_element_of_page = current_page * const.MOVE_PER_PAGE
    first_element_of_page = last_element_of_page - const.MOVE_PER_PAGE
    artwork = data.get_home_thumb_url(pokemon, is_shiny_setted)

    text = script.movepool_title.format(artwork, const.RED_SPARK, current_page, total_pages)

    for i in range(first_element_of_page, last_element_of_page):
        if i >= len(pokemon.moves):
            break

        move = pokemon_client().get_move(pokemon.moves[i].move.name).pop()
        data_dict = {
            'name': get_move_name(move),
            'class': move.damage_class.name.title(),
            'type': move.type.name.title(),
            'power': move.power if move.power else '-',
            'accuracy': move.accuracy if move.accuracy else '-',
            'emoji': const.TYPE_EMOJI[move.type.name]
        }

        text += script.move.format(**data_dict)

    return text


def get_move_page_text(move):
    data_dict = {
        'name': data.get_english_name(move.names),
        'class': move.damage_class.name.title(),
        'type': move.type.name.title(),
        'power': move.power if move.power else '-',
        'accuracy': move.accuracy if move.accuracy else '-',
        'pp': move.pp,
        'description': data.get_english_effect(move.effect_entries),
        'generation': data.prettify_name(move.generation.name),
        #'pokemon_list': data.get_pokemon_list_text(move.learned_by_pokemon),
        'type_emoji': const.TYPE_EMOJI[move.type.name],
        'move_emoji': const.GLOVE,
        'data_emoji': const.MOVE_DATA,
        'description_emoji': const.EYE,
        'pokemon_list_emoji': const.POKEMON
    }
    return script.move_page.format(**data_dict)


def get_move_name(move):
    move_name = data.get_english_name(move.names)
    return add_move_link(move, move_name)


def add_move_link(move, name_displayed):
    url = '<a href="https://t.me/{}?start=move-{}">{}</a>'
    return url.format(const.BOT_USERNAME, move.name, name_displayed)
