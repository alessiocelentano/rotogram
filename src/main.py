import re
import json

import pokepy
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent

from pokemon import pokemon_text
from moveset import moveset_text
from locations import locations_text
from markup import data_markup, moveset_markup, locations_markup


app = Client("rotogram")
pk = pokepy.V2Client()
user_dict = {}
with open("src/pkmn.json") as f:
    data = json.load(f)


@app.on_inline_query()
def main(app, inline_query):
    if len(inline_query.query) < 3:
        inline_query.answer(
            results=[],
            switch_pm_text="Help",
            switch_pm_parameter="start",
            cache_time=5
        )
        return
    matches = [pkmn.lower() for pkmn in data if inline_query.query.lower() in pkmn.lower()]
    form_list = []
    results = []
    for pkmn in matches:
        species = pk.get_pokemon_species(pkmn)[0]
        for form in data[pkmn]:
            pkmn_data = pk.get_pokemon(form)[0]
            name_id = re.findall("[0-9]+", pkmn_data.forms[0].url)[-1]
            name_list = [name.name for name in pk.get_pokemon_form(name_id)[0].names if name.language.name == "en"]
            if name_list:
                name = name_list[0]
            else:
                name = [name.name for name in species.names if name.language.name == "en"][0]
            thumb_url = pkmn_data.sprites.front_default.replace("pokemon", "pokemon/other/official-artwork")
            markup = data_markup(name, expanded=0)
            typing = " / ".join([ty.type.name.title() for ty in pkmn_data.types])
            genus = species.genera[7].genus
            form_list.append(form)
            results.append(
                InlineQueryResultArticle(
                    title=name,
                    description=f"{genus}\nType: {typing}",
                    input_message_content=InputTextMessageContent(f"🔄 Loading..."),
                    thumb_url=thumb_url,
                    reply_markup=markup
                )
            )
    user_dict[inline_query.from_user.id] = {r.id: form for r, form in zip(results, form_list)}
    inline_query.answer(results=results, cache_time=3)


@app.on_chosen_inline_result()
def chosen(app, inline_query):
    form = user_dict[inline_query.from_user.id][inline_query.result_id]
    species = [sp for sp in data if form in data[sp] or sp == form][0]
    text = pokemon_text(pk, species, form, expanded=0)
    markup = data_markup(form, expanded=0)
    app.edit_inline_text(
        inline_message_id=inline_query.inline_message_id,
        text=text,
        parse_mode="HTML",
        reply_markup=markup
    )


@app.on_callback_query(filters.create(lambda _, __, query: "infos" in query.data))
def expand(app, query):
    expanded = int(re.split("/", query.data)[1])
    form = re.split("/", query.data)[2]
    species = [sp for sp in data if form in data[sp] or sp == form][0]
    text = pokemon_text(pk, species, form, expanded=expanded)
    markup = data_markup(form, expanded=expanded)
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
    form = re.split("/", query.data)[2]
    text = moveset_text(pk, form, page)
    markup = moveset_markup(pk, form, page)
    app.answer_callback_query(query.id)
    app.edit_inline_text(
        inline_message_id=query.inline_message_id,
        text=text,
        parse_mode="HTML",
        reply_markup=markup
    )


@app.on_callback_query(filters.create(lambda _, __, query: "locations" in query.data))
def locations(app, query):
    form = re.split("/", query.data)[1]
    text = locations_text(pk, form)
    markup = locations_markup(form)
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


if __name__ == "__main__":
    app.run()
