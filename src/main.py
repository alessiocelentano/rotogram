import json
import re

from pyrogram import Client, Filters
from pyrogram import (InlineKeyboardMarkup,
                      InlineKeyboardButton,
                      CallbackQuery)

import functions as func
import raid_dynamax as raid

from Config import Config

app = Client(
    api_id=Config.aid,
    api_hash=Config.ahash,
    bot_token=Config.bot_token,
    session_name='rotomgram'
)

texts = json.load(open('src/texts.json', 'r'))
data = json.load(open('src/pkmn.json', 'r'))
stats = json.load(open('src/stats.json', 'r'))
jtype = json.load(open('src/type.json', 'r'))

usage_dict = {'vgc': None}
raid_dict = {}


# ===== Stats =====
@app.on_message(Filters.private & Filters.create(lambda _, message: str(message.chat.id) not in stats['users']))
@app.on_message(Filters.group & Filters.create(lambda _, message: str(message.chat.id) not in stats['groups']))
def get_bot_data(app, message):
    cid = str(message.chat.id)
    if message.chat.type == 'private':
        stats['users'][cid] = {}
        name = message.chat.first_name
        try:
            name = message.chat.first_name + ' ' + message.chat.last_name
        except TypeError:
            name = message.chat.first_name
        stats['users'][cid]['name'] = name
        try:
            stats['users'][cid]['username'] = message.chat.username
        except AttributeError:
            pass

    elif message.chat.type in ['group', 'supergroup']:
        stats['groups'][cid] = {}
        stats['groups'][cid]['title'] = message.chat.title
        try:
            stats['groups'][cid]['username'] = message.chat.username
        except AttributeError:
            pass
        stats['groups'][cid]['members'] = app.get_chat(cid).members_count

    json.dump(stats, open('src/stats.json', 'w'), indent=4)
    print(stats)
    print('\n\n')
    message.continue_propagation()


@app.on_message(Filters.command(['stats', 'stats@MadBoy_Rotomgram2_Bot']))
def get_stats(app, message):
    if message.from_user.id in Config.sudo:
        members = 0
        for group in stats['groups']:
            members += stats['groups'][group]['members']
        text = texts['stats'].format(
            len(stats['users']),
            len(stats['groups']),
            members
        )
        app.send_message(
            chat_id=message.chat.id,
            text=text
        )


# ===== Home =====
@app.on_message(Filters.command(['start', 'start@MadBoy_Rotomgram2_Bot']))
def start(app, message):
    app.send_message(
        chat_id=message.chat.id,
        text=texts['start_message'],
        parse_mode='HTML'
    )

    
# ==== Type Pokemon =====
@app.on_message(Filters.command(['type', 'type@MadBoy_Rotomgram2_Bot']))
def ptype(app, message):
    try:
        gtype = message.text.split(' ')[1]
    except IndexError as s:
        app.send_message(
            chat_id=message.chat.id,
            text="`Syntex error: use eg '/type fairy'`"
        )
        return
    try:
        data = jtype[gtype.lower()]
    except KeyError as s:
        app.send_message(
            chat_id=message.chat.id,
            text=("`Eeeh, LoL, This type doesn't exists :/ `\n"
                  "`Do  /types  to check for the existing types.`")
        )
        return
    strong_against = ", ".join(data['strong_against'])
    weak_against = ", ".join(data['weak_against'])
    resistant_to = ", ".join(data['resistant_to'])
    vulnerable_to = ", ".join(data['vulnerable_to'])
    keyboard = ([[
        InlineKeyboardButton('All Types',callback_data=f"hexa_back_{message.from_user.id}")]])
    app.send_message(
        chat_id=message.chat.id,
        text=(f"Type  :  `{gtype.lower()}`\n\n"
              f"Strong Against:\n`{strong_against}`\n\n"
              f"Weak Against:\n`{weak_against}`\n\n"
              f"Resistant To:\n`{resistant_to}`\n\n"
              f"Vulnerable To:\n`{vulnerable_to}`"),
        reply_markup=InlineKeyboardMarkup(keyboard)
           
    )
    
    
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
    
@app.on_message(Filters.command(['types', 'types@MadBoy_Rotomgram2_Bot']))
def types(app, message): 
    user_id = message.from_user.id
    app.send_message(
        chat_id=message.chat.id,
        text="List of types of Pokemons:",
        reply_markup=InlineKeyboardMarkup(ptype_buttons(user_id))
    )
    
    
# ===== Types Callback ====
@app.on_callback_query(Filters.create(lambda _, query: 'type_' in query.data))
def button(client: app, callback_query: CallbackQuery):
    q_data = callback_query.data
    query_data = q_data.split('_')[0]
    type_n = q_data.split('_')[1]
    user_id = int(q_data.split('_')[2])
    cuser_id = callback_query.from_user.id
    if cuser_id == user_id:
        if query_data == "type":
            data = jtype[type_n]
            strong_against = ", ".join(data['strong_against'])
            weak_against = ", ".join(data['weak_against'])
            resistant_to = ", ".join(data['resistant_to'])
            vulnerable_to = ", ".join(data['vulnerable_to'])
            keyboard = ([[
            InlineKeyboardButton('Back',callback_data=f"hexa_back_{user_id}")]])
            callback_query.message.edit_text(
                text=(f"Type  :  `{type_n}`\n\n"
                f"Strong Against:\n`{strong_against}`\n\n"
                f"Weak Against:\n`{weak_against}`\n\n"
                f"Resistant To:\n`{resistant_to}`\n\n"
                f"Vulnerable To:\n`{vulnerable_to}`"),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    else:
        callback_query.answer(
            text="You can't use this button!",
            show_alert=True
        )
    

@app.on_callback_query(Filters.create(lambda _, query: 'hexa_' in query.data))
def button2(client: app, callback_query: CallbackQuery):
    q_data = callback_query.data
    query_data = q_data.split('_')[1]
    user_id = int(q_data.split('_')[2])
    cuser_id = callback_query.from_user.id
    if user_id == cuser_id:
        if query_data == "back":
            callback_query.message.edit_text(
                "List of types of Pokemons:",
                reply_markup=InlineKeyboardMarkup(ptype_buttons(user_id))
            )
        elif query_data == "delete":
            callback_query.message.delete()
        else:
            return
    else:
        callback_query.answer(
            text="You can't use this button!",
            show_alert=True
        )
        
        
# ===== Pokemon Type Command ======
@app.on_message(Filters.command(['ptype', 'ptype@MadBoy_Rotomgram2_Bot']))
def poketypes(app, message): 
    user_id = message.from_user.id
    try:
        arg = message.text.split(' ')[1].lower()
    except IndexError:
        app.send_message(
            chat_id=message.chat.id,
            text=("`Syntex error: use eg '/ptype pokemon_name'`\n"
                  "`eg /ptype Lunala`")
        )
        return  
    try:
        p_type = data[arg][arg]['type']
    except KeyError:
        app.send_message(
            chat_id=message.chat.id,
            text="`Eeeh, LoL, This Pokemon doesn't exists :/`"
        )
        return
    
    try:
        get_pt = f"{p_type['type1']}, {p_type['type2']:}"
        keyboard = ([[
        InlineKeyboardButton(p_type['type1'],callback_data=f"poket_{p_type['type1']}_{arg}_{user_id}"),
        InlineKeyboardButton(p_type['type2'],callback_data=f"poket_{p_type['type2']}_{arg}_{user_id}")]])
    except KeyError:
        get_pt = f"{p_type['type1']}"
        keyboard = ([[
        InlineKeyboardButton(p_type['type1'],callback_data=f"poket_{p_type['type1']}_{arg}_{user_id}")]])
    app.send_message(
        chat_id=message.chat.id,
        text=(f"Pokemon: `{arg}`\n\n"
              f"Types: `{get_pt}`\n\n"
              "__Click the button below to get the info of the found type's/types' effectiveness!__"),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
@app.on_callback_query(Filters.create(lambda _, query: 'poket_' in query.data))
def poketypes_callback(client: app, callback_query: CallbackQuery):
    q_data = callback_query.data
    query_data = q_data.split('_')[1].lower()
    pt_name = q_data.split('_')[2]
    user_id = int(q_data.split('_')[3])  
    if callback_query.from_user.id == user_id:  
        data = jtype[query_data]
        strong_against = ", ".join(data['strong_against'])
        weak_against = ", ".join(data['weak_against'])
        resistant_to = ", ".join(data['resistant_to'])
        vulnerable_to = ", ".join(data['vulnerable_to'])
        keyboard = ([[
        InlineKeyboardButton('Back',callback_data=f"pback_{pt_name}_{user_id}")]])
        callback_query.message.edit_text(
            text=(f"Type  :  `{query_data}`\n\n"
            f"Strong Against:\n`{strong_against}`\n\n"
            f"Weak Against:\n`{weak_against}`\n\n"
            f"Resistant To:\n`{resistant_to}`\n\n"
            f"Vulnerable To:\n`{vulnerable_to}`"),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        callback_query.answer(
            text="You're not allowed to use this!",
            show_alert=True
        )
    
@app.on_callback_query(Filters.create(lambda _, query: 'pback_' in query.data))
def poketypes_back(client: app, callback_query: CallbackQuery):
    q_data = callback_query.data
    query_data = q_data.split('_')[1].lower()
    user_id = int(q_data.split('_')[2]) 
    if callback_query.from_user.id == user_id:
        p_type = data[query_data][query_data]['type']
        try:
            get_pt = f"{p_type['type1']}, {p_type['type2']:}"
            keyboard = ([[
            InlineKeyboardButton(p_type['type1'],callback_data=f"poket_{p_type['type1']}_{query_data}_{user_id}"),
            InlineKeyboardButton(p_type['type2'],callback_data=f"poket_{p_type['type2']}_{query_data}_{user_id}")]])
        except KeyError:
            get_pt = f"{p_type['type1']}"
            keyboard = ([[
            InlineKeyboardButton(p_type['type1'],callback_data=f"poket_{p_type['type1']}_{query_data}_{user_id}")]])
        callback_query.message.edit_text(
            (f"Pokemon: `{query_data}`\n\n"
             f"Types: `{get_pt}`\n\n"
             "__Click the button below to get the info of the found type's/types' effectiveness!__"),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        callback_query.answer(
            text="You're not allowed to use this!",
            show_alert=True
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


# ===== Usage command =====
@app.on_callback_query(filters.create(lambda _, query: "usage" in query.data))
@app.on_message(filters.command(["usage", "usage@MadBoy_Rotomgram2_Bot"]))
def usage(app, message):
    try:
        page = int(re.split("/", message.data)[1])
        dictt = func.get_usage_vgc(int(page), usage_dict["vgc"])
    except AttributeError:
        page = 1
        text = "<i>Yeah wi8, Connecting to Pokémon Showdown database...</i>"
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
