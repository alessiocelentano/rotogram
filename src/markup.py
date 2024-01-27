from math import ceil

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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


def pics_markup(thumb_type):
    return InlineKeyboardMarkup([
        [official_artworks_button(thumb_type)],
        [home_sprites_button(thumb_type)],
        [showdown_sprites_button(thumb_type)]
    ])


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
        text=const.REDUCE if is_expanded else const.EXPAND,
        callback_data=f'infos/{int(not is_expanded)}/{species_name}'
    )


def movepool(species_name):
    return InlineKeyboardButton(
        text=const.MOVEPOOL,
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
        text=const.BACK,
        callback_data=f'infos/0/{pokemon_name}'
    )


def official_artworks_button(thumb_type):
    emoji = const.TICK if thumb_type == 'official artwork' else const.X
    return InlineKeyboardButton(
        text=f'{emoji} {const.OFFICIAL_ARTWORKS}',
        callback_data='official artwork'
    )


def home_sprites_button(thumb_type):
    emoji = const.TICK if thumb_type == 'home' else const.X
    return InlineKeyboardButton(
        text=f'{emoji} {const.HOME}',
        callback_data='home'
    )


def showdown_sprites_button(thumb_type):
    emoji = const.TICK if thumb_type == 'showdown' else const.X
    return InlineKeyboardButton(
        text=f'{emoji} {const.SHOWDOWN}',
        callback_data='showdown'
    )


def dummy_expand_reduce():
    return InlineKeyboardButton(
        text=const.EXPAND,
        callback_data='dummy_prompt'
    )


def shiny_page_expand_reduce():
    return InlineKeyboardButton(
        text=const.EXPAND,
        callback_data='shiny_prompt'
    )


def accept_shiny_button():
    return InlineKeyboardButton(
        text=const.ACCEPT_SHINY_BUTTON,
        callback_data='accept_shiny'
    )
