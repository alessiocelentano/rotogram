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
    tiers = [0, 9, 19, 39, 79, 89, 99, 114, 129, 149, 256]
    emoji_dict = {}
    for stat in stats:
        rating_emoji = ""
        rating_n = 0
        for i in tiers:
            if base < i:
                while rating_n >= 2:
                    rating_emoji += "🌕"
                    rating_n -= 2
                if rating_n == 1:
                    rating_emoji += "🌗"
                while len(rating_emoji) != 5:
                    rating_emoji += "🌑"
                break
            else:
                rating_n += 1
        emoji_dict[stat] = rating_emoji
    return rating_emoji
