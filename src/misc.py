from client import pokemon_client


def get_english_genus(genus_name_list):
    for name in genus_name_list:
        if name.language.name == 'en': return name.genus


def get_english_name_of(element):
    for name in element.names:
        if name.language.name == 'en': return name.name


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
    if is_shiny:
        return thumb_url.replace('pokemon', 'pokemon/other/home/shiny')
    else:
        return thumb_url.replace('pokemon', 'pokemon/other/home')
