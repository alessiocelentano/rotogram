import re

import pokepy
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent

from pokemon import pokemon_text
from moveset import moveset_text
from locations import locations_text
from markup import data_markup, moveset_markup


app = Client("Debug")
pk = pokepy.V2Client()


@app.on_inline_query()
def main(app, inline_query):
    try:
        pokemon = pk.get_pokemon_species(inline_query.query)
        thumb_url = pk.get_pokemon(inline_query.query).sprites.front_default.replace("pokemon", "pokemon/other/official-artwork")
        name = pokemon.names[7].name
        inline_query.answer(
            results=[
                InlineQueryResultArticle(
                    title=name,
                    input_message_content=InputTextMessageContent(
                        pokemon_text(pk, name, expanded=0)
                    ),
                    thumb_url=thumb_url,
                    reply_markup=data_markup(name, expanded=0)
                )
            ],
            cache_time=5
        )
    except Exception:
        inline_query.answer(
            results=[],
            switch_pm_text="Help",
            switch_pm_parameter="start",
            cache_time=5
        )


@app.on_callback_query(filters.create(lambda _, __, query: "infos" in query.data))
def expand(app, query):
    expanded = int(re.split("/", query.data)[1])
    pkmn = re.split("/", query.data)[2]
    text = pokemon_text(pk, pkmn, expanded=expanded)
    markup = data_markup(pkmn, expanded=expanded)
    app.answer_callback_query(query.id)
    app.edit_inline_text(
        inline_message_id=query.inline_message_id,
        text=text,
        parse_mode="HTML",
        reply_markup=markup
    )


@app.on_callback_query(filters.create(lambda _, __, query: "moveset" in query.data))
def moveset(app, query):
    page = int(re.split("/", query.data)[1])
    pkmn = re.split("/", query.data)[2]
    text = moveset_text(pk, pkmn, page)
    markup = moveset_markup(pk, pkmn, page)
    app.answer_callback_query(query.id)
    app.edit_inline_text(
        inline_message_id=query.inline_message_id,
        text=text,
        parse_mode="HTML",
        reply_markup=markup
    )


@app.on_message(filters.command("start"))
def start(app, message):
    text = """⚡️ <b><u>What is Rotogram?</u></b>
Rotomgram is a bot which acts as a helper for trainers on Telegram. \
You can check information of Pokemon, Showdown usage and more as quickly as possible, without ever leaving Telegram\n
🛠 <b><u>Usage</u></b>
Just write Pokemon name after @rotogrambot (e.g.: @rotogrambot Rotom)\n
@alessiocelentano | <a href="t.me/rotogram">Follow us</a> | <a href="github.com/alessiocelentano/rotogram">GitHub</a>"""
    app.send_message(
        chat_id=message.from_user.id,
        text=text
    )

"""

@app.on_callback_query(filters.create(lambda _, __, query: "locations" in query.data))
def locations(app, call):
    pkmn = re.split("/", call.data)[2]
    pkmn_data = pk.get_pokemon(pkmn)
    page = int(re.split("/", call.data)[1])
    pages = (len(pkmn_data.moves) // 10) + 1
    maxx = page * 10
    minn = maxx - 10
    text = get_locations(data, pkmn)

    markup = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            text="⚔️ Moveset",
            callback_data="moveset/"+pkmn+"/"+form
        )
    ],
    [
        InlineKeyboardButton(
            text="🔙 Back to basic infos",
            callback_data="basic_infos/"+pkmn+"/"+form
        )
    ]])

    func.bot_action(app, call, text, markup)
"""


app.run()
