import re

import pokepy as pk

from evolutions import get_evolutions
from abilities import get_abilities
from emoji import typing_emoji, stats_rating_emoji


def get_base_data(pkmn):
    pkmn_data = pk.get_pokemon(pkmn)
    species = pk.get_pokemon_species(pkmn)

    name = species.name.title()
    artwork_link = pkmn_data.sprites.front_default.replace("pokemon", "pokemon/other/official-artwork")
    emoji = typing_emoji(pkmn_data)
    dex_number = species.order
    types = [ty.type.name.title() for ty in pkmn_data.types]
    types_text = " / ".join(types)
    abilities = get_abilities(pkmn_data)
    abilities_text = " / ".join(abilities["abilities"])
    hidden_ability = abilities["hidden_ability"] if abilities["hidden_ability"] else "---"
    evolutions = get_evolutions(species)
    evolution_text = get_evolution_text(evolutions)
    stats = {stat.stat.name: stat.base_stat for stat in pkmn_data.stats}
    rating = stats_rating_emoji(stats)

    text = f"""<u>{name}</u> <a href="{artwork_link}">{emoji}</a>\n
<b>National</b>: {dex_number}
<b>Type</b>: {types_text}
<b>Abilities</b>: {abilities_text}
<b>Hidden Ability</b>: {hidden_ability}
{evolution_text}
<b><u>Base stats</u></b>:
{stats["hp"]} HP {rating["hp"]}
{stats["attack"]} ATK {rating["attack"]}
{stats["defense"]} DEF {rating["defense"]}
{stats["special-attack"]} SPA {rating["special-attack"]}
{stats["special-defense"]} SPD {rating["special-defense"]}
{stats["speed"]} SPE {rating["speed"]}
"""
    return text


"""
def get_advanced_data(pkmn):
    base_friendship = pkmn["base_friendship"]["value"]
    catch_rate = pkmn["catch_rate"]["value"]
    growth_rate = pkmn["growth_rate"]
    egg_cycles = pkmn["egg_cycles"]
    species = pkmn["species"]

    gender = ""
    if pkmn["gender"]["genderless"]:
        gender += "Genderless"
    else:
        for i, j in list(pkmn["gender"].items()):
            if j == "100%":
                gender = i + ": " + j + "\n"
            elif type(j) == bool:
                continue
            else:
                gender += i + ": " + j + "\n"
        gender = gender[:-1]

    ev_yield = ""
    for i in pkmn["ev_yield"]:
        ev_yield += " / " + pkmn["ev_yield"][i] + " " + i.title()
    ev_yield = ev_yield[3:]

    egg_groups = ""
    for i in pkmn["egg_groups"]:
        egg_groups += " / " + i
    egg_groups = egg_groups[3:]

    other_lang = ""
    for i, j in pkmn["other_lang"].items():
        other_lang += "\n" + i.title() + ": " + j
    other_lang = other_lang[1:]

    name_origin = ""
    for i, j in pkmn["name_origin"].items():
        name_origin += ", " + i + " (" + j + ")"
    name_origin = name_origin[2:]

    tmp = pkmn["height"]
    height = tmp["si"] + " (" + tmp["usc"] + ")"
    tmp = pkmn["weight"]
    weight = tmp["si"] + " (" + tmp["usc"] + ")"

    return {
        "base_friendship": base_friendship,
        "catch_rate": catch_rate,
        "growth_rate": growth_rate,
        "egg_cycles": egg_cycles,
        "species": species,
        "gender": gender,
        "ev_yield": ev_yield,
        "egg_group": egg_groups,
        "other_lang": other_lang,
        "name_origin": name_origin,
        "height": height,
        "weight": weight
    }


def set_message(pkmn, *args, reduced=None):
    if reduced:
        text = texts["reduced_text"]
        base_data = get_base_data(pkmn, args)
        return text.format(**base_data)
    else:
        text = texts["expanded_text"]
        base_data = get_base_data(pkmn, args)
        advanced_data = get_advanced_data(pkmn)
        return text.format(**base_data, **advanced_data)
"""
