import json
import re

import pokepy
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


texts = json.load(open("src/texts.json", "r"))
usage_dict = {"vgc": None}
app = Client("Debug")
pk = pokepy.V2Client()


# ===== Home =====
@app.on_message(filters.command(["start", "start@MadBoy_Rotomgram2_Bot"]))
def start(app, message):
    app.send_message(
        chat_id=message.chat.id,
        text=texts["start_message"],
        parse_mode="HTML"
    )


# ===== Data command =====
@app.on_callback_query(filters.create(lambda _, query: "basic_infos" in query.data))
@app.on_message(filters.command(["data", "data@MadBoy_Rotomgram2_Bot"]))
def pkmn_search(app, message):
    try:
        if re.match("/data(@MadBoy_Rotomgram2_Bot)*", message.text):
            app.send_message(message.chat.id, texts["error1"], parse_mode="HTML")
            return None
        pkmn = message.text
    except AttributeError:
        pkmn = re.split("/", message.data)[1]

    if pkmn in form:
        text = func.set_message(data[pkmn][form], reduced=True)
    else:
        base_form = re.sub("_", " ", pkmn.title())
        name = base_form + " (" + data[pkmn][form]["name"] + ")"
        text = func.set_message(data[pkmn][form], name, reduced=True)

    markup_list = [[
        InlineKeyboardButton(
            text="➕ Expand",
            callback_data="all_infos/"+pkmn+"/"+form
        )
    ],
    [
        InlineKeyboardButton(
            text="⚔️ Moveset",
            callback_data="moveset/"+pkmn+"/"+form
        ),
        InlineKeyboardButton(
            text="🏠 Locations",
            callback_data="locations/"+pkmn+"/"+form
        )
    ]]
    for alt_form in data[pkmn]:
        if alt_form != form:
            markup_list.append([
                InlineKeyboardButton(
                    text=data[pkmn][alt_form]["name"],
                    callback_data="basic_infos/"+pkmn+"/"+alt_form
                )
            ])
    markup = InlineKeyboardMarkup(markup_list)

    func.bot_action(app, message, text, markup)


def best_matches(app, message, result):
    text = texts["results"]
    emoji_list = ["1️⃣", "2️⃣", "3️⃣"]
    index = 0
    for dictt in result:
        pkmn = dictt["pkmn"]
        form = dictt["form"]
        percentage = dictt["percentage"]
        form_name = data[pkmn][form]["name"]
        name = func.form_name(pkmn.title(), form_name)
        text += "\n{} <b>{}</b> (<i>{}</i>)".format(
            emoji_list[index],
            name,
            percentage
        )
        if index == 0:
            text += " [<b>⭐️ Top result</b>]"
        index += 1
    app.send_message(message.chat.id, text, parse_mode="HTML")


@app.on_callback_query(filters.create(lambda _, query: "all_infos" in query.data))
def all_infos(app, call):
    pkmn = re.split("/", call.data)[1]
    form = re.split("/", call.data)[2]
    
    if pkmn in form:
        text = func.set_message(data[pkmn][form], reduced=False)
    else:
        base_form = re.sub("_", " ", pkmn.title())
        name = base_form + " (" + data[pkmn][form]["name"] + ")"
        text = func.set_message(data[pkmn][form], name, reduced=False)

    markup_list = [[
        InlineKeyboardButton(
            text="➖ Reduce",
            callback_data="basic_infos/"+pkmn+"/"+form
        )
    ],
    [
        InlineKeyboardButton(
            text="⚔️ Moveset",
            callback_data="moveset/"+pkmn+"/"+form
        ),
        InlineKeyboardButton(
            text="🏠 Locations",
            callback_data="locations/"+pkmn+"/"+form
        )
    ]]
    for alt_form in data[pkmn]:
        if alt_form != form:
            markup_list.append([
                InlineKeyboardButton(
                    text=data[pkmn][alt_form]["name"],
                    callback_data="basic_infos/"+pkmn+"/"+alt_form
                )
            ])
    markup = InlineKeyboardMarkup(markup_list)

    func.bot_action(app, call, text, markup)


@app.on_callback_query(filters.create(lambda _, query: "moveset" in query.data))
def moveset(app, call):
    pkmn = re.split("/", call.data)[1]
    form = re.split("/", call.data)[2]
    if len(re.split("/", call.data)) == 4:
        page = int(re.split("/", call.data)[3])
    else:
        page = 1
    dictt = func.set_moveset(pkmn, form, page)

    func.bot_action(app, call, dictt["text"], dictt["markup"])


@app.on_callback_query(filters.create(lambda _, query: "locations" in query.data))
def locations(app, call):
    pkmn = re.split("/", call.data)[1]
    form = re.split("/", call.data)[2]

    text = func.get_locations(data, pkmn)

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


# ==== Types List =====
def ptype_buttons(user_id):
    keyboard = ([[
        InlineKeyboardButton('Normal',callback_data=f"type_normal_{user_id}"),
        InlineKeyboardButton('Fighting',callback_data=f"type_fighting_{user_id}"),
        InlineKeyboardButton('Flying',callback_data=f"type_flying_{user_id}")]])
    keyboard += ([[
        InlineKeyboardButton('Poison',callback_data=f"type_poison_{user_id}"),
        InlineKeyboardButton('Ground',callback_data=f"type_ground_{user_id}"),
        InlineKeyboardButton('Rock',callback_data=f"type_rock_{user_id}")]])
    keyboard += ([[
        InlineKeyboardButton('Bug',callback_data=f"type_bug_{user_id}"),
        InlineKeyboardButton('Ghost',callback_data=f"type_ghost_{user_id}"),
        InlineKeyboardButton('Steel',callback_data=f"type_steel_{user_id}")]])
    keyboard += ([[
        InlineKeyboardButton('Fire',callback_data=f"type_fire_{user_id}"),
        InlineKeyboardButton('Water',callback_data=f"type_water_{user_id}"),
        InlineKeyboardButton('Grass',callback_data=f"type_grass_{user_id}")]])
    keyboard += ([[
        InlineKeyboardButton('Electric',callback_data=f"type_electric_{user_id}"),
        InlineKeyboardButton('Psychic',callback_data=f"type_psychic_{user_id}"),
        InlineKeyboardButton('Ice',callback_data=f"type_ice_{user_id}")]])
    keyboard += ([[
        InlineKeyboardButton('Dragon',callback_data=f"type_dragon_{user_id}"),
        InlineKeyboardButton('Fairy',callback_data=f"type_fairy_{user_id}"),
        InlineKeyboardButton('Dark',callback_data=f"type_dark_{user_id}")]])
    keyboard += ([[
        InlineKeyboardButton('Delete',callback_data=f"hexa_delete_{user_id}")]])
    return keyboard

# ===== Usage command =====
@app.on_callback_query(filters.create(lambda _, query: "usage" in query.data))
@app.on_message(filters.command(["usage", "usage@MadBoy_Rotomgram2_Bot"]))
def usage(app, message):
    try:
        page = int(re.split("/", message.data)[1])
        dictt = func.get_usage_vgc(int(page), usage_dict["vgc"])
    except AttributeError:
        page = 1
        text = "<i>Connecting to Pokémon Showdown database...</i>"
        message = app.send_message(message.chat.id, text, parse_mode="HTML")
        dictt = func.get_usage_vgc(int(page))
        usage_dict["vgc"] = dictt["vgc_usage"]

    leaderboard = dictt["leaderboard"]
    base_text = texts["usage"]
    text = ""
    for i in range(15):
        pkmn = leaderboard[i]
        text += base_text.format(
            pkmn["rank"],
            pkmn["pokemon"],
            pkmn["usage"],
        )
    markup = dictt["markup"]

    func.bot_action(app, message, text, markup)


# ===== FAQ command =====
@app.on_message(filters.command(["faq", "faq@MadBoy_Rotomgram2_Bot"]))
def faq(app, message):
    app.send_message(
        chat_id=message.chat.id,
        text=texts["faq"],
        parse_mode="HTML",
        disable_web_page_preview=True
    )


# ===== About command =====
@app.on_message(filters.command(["about", "about@MadBoy_Rotomgram2_Bot"]))
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
