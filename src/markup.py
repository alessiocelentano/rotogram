from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def data_markup(pkmn, expanded):
    if expanded:
        first_button_text = "➖ Reduce"
        first_button_callback_data = "infos/0/" + pkmn
    else:
        first_button_text = "➕ Expand"
        first_button_callback_data = "infos/1/" + pkmn
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(
            text=first_button_text,
            callback_data=first_button_callback_data
        )
    ], [
        InlineKeyboardButton(
            text="⚔️ Moveset",
            callback_data="moveset/1/" + pkmn
            # 1 => page number, 10 moves each page (see set_moveset())
        )
    ], [
        InlineKeyboardButton(
            text="🏠 Locations",
            callback_data="locations/" + pkmn
        )
    ]])


def moveset_markup(pk, pkmn, page):
    pkmn_data = pk.get_pokemon(pkmn)[0]
    pages = (len(pkmn_data.moves) // 10) + 1
    # Initialize buttons
    markup_list = []
    begin = InlineKeyboardButton(
        text="<<1",
        callback_data="moveset/1/"+pkmn
    )
    pre = InlineKeyboardButton(
        text=str(page-1),
        callback_data="moveset/"+str(page-1)+"/"+pkmn
    )
    page_button = InlineKeyboardButton(
        text="•"+str(page)+"•",
        callback_data="moveset/"+str(page)+"/"+pkmn
    )
    suc = InlineKeyboardButton(
        text=str(page+1),
        callback_data="moveset/"+str(page+1)+"/"+pkmn
    )
    end = InlineKeyboardButton(
        text=str(pages)+">>",
        callback_data="moveset/"+str(pages)+"/"+pkmn
    )

    # Create a page index that display, when possible,
    # First page, previous page, current page, next page, last page
    markup_list.append([])
    if 1 < page-1:
        markup_list[0].append(begin)
    if page != 1:
        markup_list[0].append(pre)
    if markup_list[0] or page != pages:
        markup_list[0].append(page_button)
    if page != pages:
        markup_list[0].append(suc)
    if pages > page+1:
        markup_list[0].append(end)
    if not markup_list[0]:
        markup_list.remove(markup_list[0])

    markup_list.append([
        InlineKeyboardButton(
            text="🔙 Back",
            callback_data="infos/0/" + pkmn
        )
    ])

    return InlineKeyboardMarkup(markup_list)


def locations_markup(pkmn):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(
            text="🔙 Back",
            callback_data="infos/0/" + pkmn
        )
    ]])

