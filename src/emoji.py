def typing_emoji(pkmn_data):
    typing = pkmn_data.types[0].type.name.title()
    if typing == "Grass":
        return "🌱"
    elif typing == "Fire":
        return "🔥"
    elif typing == "Water":
        return "💧"
    elif typing == "Flying":
        return "🦅"
    elif typing == "Bug":
        return "🐞"
    elif typing == "Normal":
        return "🐾"
    elif typing == "Dragon":
        return "🐲"
    elif typing == "Ice":
        return "❄️"
    elif typing == "Ghost":
        return "👻"
    elif typing == "Fighting":
        return "💪"
    elif typing == "Fairy":
        return "🌸"
    elif typing == "Steel":
        return "⚙️"
    elif typing == "Dark":
        return "🌙"
    elif typing == "Psychic":
        return "🔮"
    elif typing == "Electric":
        return "⚡️"
    elif typing == "Ground":
        return "🌍"
    elif typing == "Rock":
        return "🗻"
    elif typing == "Poison":
        return "☠️"


def stats_rating_emoji(stats):
    emoji_dict = {}
    for stat in stats:
        if stats[stat] < 20:
            rating_emoji = "🔴"
        elif stats[stat] < 50:
            rating_emoji = "🟠🟠"
        elif stats[stat] < 80:
            rating_emoji = "🟡🟡🟡"
        elif stats[stat] < 100:
            rating_emoji = "🟢🟢🟢🟢"
        elif stats[stat] < 130:
            rating_emoji = "🔵🔵🔵🔵🔵"
        else:
            rating_emoji = "🟣🟣🟣🟣🟣🟣"
        emoji_dict[stat] = rating_emoji
    return emoji_dict
