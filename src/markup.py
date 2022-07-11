from math import ceil

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import script
import const


def datapage_markup(pokemon_name, is_expanded=False):
    return InlineKeyboardMarkup([
        [expand_reduce(pokemon_name, is_expanded)],
        [movepool(pokemon_name)]
    ])


def movepool_markup(pokemon, current_page):
    total_pages = ceil(len(pokemon.moves) / const.MOVE_PER_PAGE)
    markup_list = [[]]

    # Create a page index that display, when possible:
    # First page, previous page, current page, next page, last page
    if current_page-1 > 1:
        markup_list[0].append(begin_page(pokemon.name))
    if current_page != 1:
        markup_list[0].append(page(current_page-1, pokemon.name))
    if markup_list[0] or current_page != total_pages:
        markup_list[0].append(page(current_page, pokemon.name, mark=True))
    if current_page != total_pages:
        markup_list[0].append(page(current_page+1, pokemon.name))
    if total_pages > current_page+1:
        markup_list[0].append(ending_page(total_pages, pokemon.name))
    if not markup_list[0]:
        markup_list.remove(markup_list[0])

    markup_list.append([back(pokemon.name)])
    return InlineKeyboardMarkup(markup_list)


def dummy_prompt():
    # It's used for an useless botton when accessing to the shiny page
    return InlineKeyboardMarkup([
        [dummy_expand_reduce()],
    ])


def shiny_prompt():
    return InlineKeyboardMarkup([
        [shiny_page_expand_reduce()],
    ])


def accept_shiny():
    return InlineKeyboardMarkup([
        [accept_shiny_button()],
    ])


# === BUTTONS ===


def expand_reduce(species_name, is_expanded):
    return InlineKeyboardButton(
        text=script.reduce if is_expanded else script.expand,
        callback_data=f'infos/{int(not is_expanded)}/{species_name}'
    )


def movepool(species_name):
    return InlineKeyboardButton(
        text=script.movepool,
        callback_data=f'movepool/1/{species_name}'
        # 1 => page number, 10 moves each page (see set_moveset())
    )


def begin_page(pokemon_name):
    return InlineKeyboardButton(
        text='<<1',
        callback_data=f'movepool/1/{pokemon_name}'
    )


def page(page, pokemon_name, mark=False):
    return InlineKeyboardButton(
        text=str(page) if not mark else f'•{str(page)}•',
        callback_data=f'movepool/{page}/{pokemon_name}'
    )


def ending_page(total_pages, pokemon_name):
    return InlineKeyboardButton(
        text=f'{total_pages}>>',
        callback_data=f'movepool/{total_pages}/{pokemon_name}'
    )


def back(pokemon_name):
    return InlineKeyboardButton(
        text=script.back,
        callback_data=f'infos/0/{pokemon_name}'
    )


def dummy_expand_reduce():
    return InlineKeyboardButton(
        text=script.expand,
        callback_data='dummy_prompt'
    )


def shiny_page_expand_reduce():
    return InlineKeyboardButton(
        text=script.expand,
        callback_data='shiny_prompt'
    )


def accept_shiny_button():
    return InlineKeyboardButton(
        text=script.accept_shiny_button,
        callback_data='accept_shiny'
    )
