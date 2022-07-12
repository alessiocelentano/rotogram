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
            'name': data.get_english_name(move),
            'class': move.damage_class.name.title(),
            'type': move.type.name.title(),
            'emoji': const.TYPE_EMOJI[move.type.name],
            'power': move.power if move.power else '-',
            'accuracy': move.accuracy if move.accuracy else '-'
        }

        text += script.move.format(**data_dict)

    return text
