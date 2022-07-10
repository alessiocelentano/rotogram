import asyncio

from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent

import markup
import script
import const


def is_shiny_keyword(pokemon_name):
    return pokemon_name == const.SHINY_KEYWORD


async def load_shiny_page(app, inline_query, is_shiny_unlocked):
    await asyncio.sleep(3)
    await app.edit_inline_text(
        inline_message_id=inline_query.inline_message_id,
        text=f'{script.loading}?',
        reply_markup=markup.dummy_prompt()
    )
    await asyncio.sleep(3)
    await app.edit_inline_text(
        inline_message_id=inline_query.inline_message_id,
        text=f'{script.shiny_page_loading}',
        reply_markup=markup.dummy_prompt()
    )
    await asyncio.sleep(3)
    await app.edit_inline_text(
        inline_message_id=inline_query.inline_message_id,
        text=f'{script.shiny_page}',
        reply_markup=markup.shiny_prompt() if not is_shiny_unlocked else None
    )


def show_shiny_query():
    name = const.SHINY_PAGE_TITLE
    genus = f'{const.GLYPH_NOT_FOUND * 6} Pokémon'
    typing = const.SHINY_PAGE_TYPING
    thumb_url = const.SHINY_PAGE_THUMB_URL
    reply_markup = markup.dummy_prompt()
    return [InlineQueryResultArticle(
        title=name,
        description=f'{genus}\nType: {typing}',
        input_message_content=InputTextMessageContent(script.loading),
        thumb_url=thumb_url,
        reply_markup=reply_markup
    )]
