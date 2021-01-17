from emoji import typing_emoji


def moveset_text(pk, pkmn, page):
    pkmn_data = pk.get_pokemon(pkmn)
    pages = (len(pkmn_data.moves) // 10) + 1
    maxx = page * 10
    minn = maxx - 10
    artwork = pkmn_data.sprites.front_default.replace("pokemon", "pokemon/other/official-artwork")
    text = f"<a href=\"{artwork}\">💥</a> <u><b>Moveset ({page}/{pages})</b></u>\n\n"
    for i in range(minn, maxx):
        if i < len(pkmn_data.moves):
            move = pk.get_move(pkmn_data.moves[i].move.name)
            name = move.names[7].name
            clss = move.damage_class.name.title()
            typee = move.type.name.title()
            emoji = typing_emoji(typee)
            text += f"<a href=\"{artwork}\">{emoji}</a> <b>{name}</b> ({clss})\n"
    return text
