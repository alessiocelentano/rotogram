from math import ceil

from client import pokemon_client
from misc import get_english_name_of, get_thumb_url
from script import add_movepool_title, add_movepool_line
import const


def get_text(pokemon, current_page):
    text = ''
    total_pages = ceil(len(pokemon.moves) / const.MOVE_PER_PAGE)
    last_element_of_page = current_page * const.MOVE_PER_PAGE
    first_element_of_page = last_element_of_page - const.MOVE_PER_PAGE
    artwork = get_thumb_url(pokemon)
    text += add_movepool_title(current_page, total_pages, artwork)

    for i in range(first_element_of_page, last_element_of_page):
        if i >= len(pokemon.moves): break
        move = pokemon_client.get_move(pokemon.moves[i].move.name).pop()
        name = get_english_name_of(move)
        class_ = move.damage_class.name.title()
        type_ = move.type.name.title()
        power = move.power if move.power else '-'
        accuracy = move.accuracy if move.accuracy else '-'
        text += add_movepool_line(name, class_, type_, power, accuracy)

    return text
