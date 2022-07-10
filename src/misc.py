import re

from client import pokemon_client

import const


def get_english_genus(genus_name_list):
    for name in genus_name_list:
        if name.language.name == 'en': return name.genus


def get_english_name_of(element):
    for name in element.names:
        if name.language.name == 'en': return name.name


def get_pokemon_name(pokemon, species):
    species_name = get_english_name_of(species)
    pokemon_name_elements = pokemon.name.split('-')
    species_name_elements = species.name.split('-')
    form_name_elements = [elem for elem in pokemon_name_elements if elem not in species_name_elements]

    if not form_name_elements: return species_name

    for form in const.MAIN_ALTERNATIVE_FORMS:
        if form not in form_name_elements: continue
        form_name = const.MAIN_ALTERNATIVE_FORMS[form]
        mega_version = form_name_elements[-1] if form_name_elements[-1] in ['x', 'y'] else ''
        return f'{form_name} {species_name} {mega_version.title()}'

    return f'{species_name} ({" ".join(form_name_elements).title()})'


def get_default_pokemon_from_species(species):
    for variety in species.varieties:
        if not variety.is_default: continue
        pokemon_name = variety.pokemon.name
        return pokemon_client.get_pokemon(pokemon_name).pop()


def get_formatted_typing(pokemon):
    types = [t.type.name for t in pokemon.types]
    return ' / '.join(types).title()


def get_thumb_url(pokemon, is_shiny=False):
    thumb_url = pokemon.sprites.front_default
    if not thumb_url:
        return None
    if is_shiny:
        return thumb_url.replace('pokemon', 'pokemon/other/home/shiny')
    else:
        return thumb_url.replace('pokemon', 'pokemon/other/home')
