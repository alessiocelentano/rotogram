def moveset_text(pkmn_data, maxx, minn):
    text = "<i>Move (Type)\nCategory, Method</i>\n\n"
    artwork = pkmn_data.sprites.front_default.replace("pokemon", "pokemon/other/official-artwork")
    move_list = []
    for move in pkmn_data.moves:
        move_list.append({
            "name": move.move.name.title(),
            "type": move.move.type.title(),
            "class": move.move.damaga_class.title(),
            "emoji": typing_emoji(pkmn_data)
        })
    for i in range(minn, maxx):
        emoji = move["emoji"]
        move = move_list[i]
        name = move["name"]
        typee = move["type"]
        clss = move["class"]
        text += f"<a href=\"{artwork}\">{emoji}</a> <b>{name}</b> ({typee})\n<i>{clss}</i>\n"
    return text

