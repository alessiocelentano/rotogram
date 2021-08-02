import requests
import re


def make_readable(locations_list, artwork):
    areas = {}
    for location in locations_list:
        name = location["location_area"]["name"].title().replace("-", " ")
        if "All" in name:  # e.g.: All Rattata Area
            continue
        name = re.sub(" (Area)|(Unknown)\s*", "", name)
        area = re.sub("([A-Z]*[1-9]+F)|Route [0-9]+.*", "", name)
        location_name = name.replace(area, "")
        if area not in areas:
            areas[area] = []
        areas[area].append(location_name)
    text = f"<b><a href=\"{artwork}\">🏠</a> <u>Locations</u></b>\n\n"
    if areas:
        for area in areas:
            text += "- " + area
            text += ", ".join(areas[area])
            text += "\n"
    else:
        text += "<i>No location available for this Pokémon</i>"
    return text


def locations_text(pk, pkmn):
    pkmn_data = pk.get_pokemon(pkmn)[0]
    artwork = pkmn_data.sprites.front_default.replace("pokemon", "pokemon/other/official-artwork")
    link = pkmn_data.location_area_encounters
    locations_list = requests.get(link).json()
    text = make_readable(locations_list, artwork)
    return text
