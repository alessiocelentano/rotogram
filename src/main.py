import json
import re

import pokepy
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent
from pyrogram.types import InlineQuery, User

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
            cache_time=1
        )
    except Exception:
        # TODO: add help button
        inline_query.answer(results=[])


@app.on_callback_query(filters.create(lambda _, __, query: "infos" in query.data))
def pkmn_search(app, message):
    try:
        # on_message
        pkmn = re.sub("/data(@rotogrambot)* ", "", message.text)
        text = pokemon_text(pk, pkmn, expanded=0)
        markup = data_markup(pkmn, expanded=0)
        app.send_message(
            chat_id=message.chat.id,
            text=text,
            parse_mode='HTML',
            reply_markup=markup
        )
    except AttributeError:
        # on_callback_query
        expanded = re.split("/", message.data)[1]
        pkmn = re.split("/", message.data)[2]
        text = pokemon_text(pk, pkmn, expanded=expanded)
        markup = data_markup(pkmn, expanded=expanded)
        app.answer_callback_query(message.id)
        app.edit_message_text(
            chat_id=message.message.chat.id,
            text=text,
            message_id=message.message.message_id,
            parse_mode='HTML',
            reply_markup=markup
        )


@app.on_callback_query(filters.create(lambda _, __, query: "moveset" in query.data))
def moveset(app, call):
    pkmn = re.split("/", call.data)[2]
    pkmn_data = pk.get_pokemon(pkmn)
    page = int(re.split("/", call.data)[1])
    pages = (len(pkmn_data.moves) // 10) + 1
    maxx = page * 10
    minn = maxx - 10
    text = set_moveset(pkmn_data, maxx, minn)
    markup = moveset_markup(pkmn, page, pages)
    app.answer_callback_query(message.id)
    app.edit_message_text(
        chat_id=message.message.chat.id,
        text=text,
        message_id=message.message.message_id,
        parse_mode='HTML',
        reply_markup=markup
    )


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


@app.on_message(filters.command(["faq", "faq@RotomgramBot"]))
def faq(app, message):
    app.send_message(
        chat_id=message.chat.id,
        text=texts["faq"],
        parse_mode="HTML",
        disable_web_page_preview=True
    )


@app.on_message(filters.command(["about", "about@RotomgramBot"]))
def about(app, message):
    markup = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            text="Github",
            url="https://github.com/alessiocelentano/rotomgram"
        )
    ]])

    app.send_message(
        chat_id=message.chat.id,
        text=texts["about"],
        reply_markup=markup,
        disable_web_page_preview=True
    )


app.run()
