import re

from evolutions import get_evolutions
from emoji import typing_emoji, stats_rating_emoji
from misc import get_abilities, get_gender_percentage, stat_abbr


def get_base_data(pk, pkmn_data, species_data, extra_data):
    name_id = re.findall("[0-9]+", pkmn_data.forms[0].url)[-1]
    name_list = [name.name for name in pk.get_pokemon_form(name_id)[0].names if name.language.name == "en"]
    if name_list:
        name = name_list[0]
    else:
        name = [name.name for name in species_data.names if name.language.name == "en"][0]
    artwork_link = pkmn_data.sprites.front_default.replace("pokemon", "pokemon/other/official-artwork")
    dex_number = species_data.order
    types = [ty.type.name.title() for ty in pkmn_data.types]
    types_text = " / ".join(types)
    emoji = typing_emoji(types[0])
    abilities = get_abilities(pkmn_data)
    abilities_text = " / ".join(abilities["abilities"])
    hidden_ability = abilities["hidden_ability"] if abilities["hidden_ability"] else "---"
    evolution_text = get_evolutions(pk, species_data)
    stats = {stat.stat.name: stat.base_stat for stat in pkmn_data.stats}
    rating = stats_rating_emoji(stats)
    genus = species_data.genera[7].genus
    height = str(pkmn_data.height / 10) + " m"
    weight = str(pkmn_data.weight / 10) + " kg"
    text = f"""<b><u>{name}</u></b> <a href="{artwork_link}">{emoji}</a>
<b>Species</b>: {genus}
<b>National Dex number</b>: {dex_number}
<b>Type</b>: {types_text}
<b>Abilities</b>: {abilities_text}
<b>Hidden Ability</b>: {hidden_ability}
<b>Height</b>: {height}
<b>Weight</b>: {weight}

<b><u>Evolutions</u></b>
{evolution_text}
{extra_data}
<b><u>Base stats</u></b>
{stats["hp"]} HP {rating["hp"]}
{stats["attack"]} ATK {rating["attack"]}
{stats["defense"]} DEF {rating["defense"]}
{stats["special-attack"]} SPA {rating["special-attack"]}
{stats["special-defense"]} SPD {rating["special-defense"]}
{stats["speed"]} SPE {rating["speed"]}
    """
    return text


def get_advanced_data(pkmn_data, species_data):
    gender_percentage = get_gender_percentage(species_data)
    base_friendship = species_data.base_happiness
    ev_yield = {stat_abbr(stat.stat.name): stat.effort for stat in pkmn_data.stats if stat.effort != 0}
    ev_yield_text = " / ".join([str(ev_yield[stat]) + " " + stat for stat in ev_yield])
    catch_rate = species_data.capture_rate
    growth_rate = species_data.growth_rate.name.title().replace("-", " ")
    egg_groups = [group.name.title().replace("-", " ") for group in species_data.egg_groups]
    egg_groups_text = " / ".join(egg_groups)
    egg_cycles = species_data.hatch_counter
    text = f"""\n<b><u>Games data</u></b>
<b>Gender (male/female)</b>: {gender_percentage}
<b>Base friendship</b>: {base_friendship}
<b>EV yield</b>: {ev_yield_text}
<b>Catch rate</b>: {catch_rate}
<b>Growth rate</b>: {growth_rate}
<b>Egg groups</b>: {egg_groups_text}
<b>Egg cycles</b>: {egg_cycles}
"""
    return text


def pokemon_text(pk, species, form, expanded):
    pkmn_data = pk.get_pokemon(form)[0]
    species_data = pk.get_pokemon_species(species)[0]
    extra_data = get_advanced_data(pkmn_data, species_data) if expanded else ""
    return get_base_data(pk, pkmn_data, species_data, extra_data)
