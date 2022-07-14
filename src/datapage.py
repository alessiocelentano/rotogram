from pokepy import V2Client as pokemon_client

import data
import script
import const


def get_datapage_text(pokemon, is_expanded, is_shiny_setted=False):
    species = pokemon_client().get_pokemon_species(pokemon.species.name).pop()

    data_dict = {
        'pokemon_full_name': data.get_pokemon_full_name(pokemon, species),
        'artwork_url': data.get_home_thumb_url(pokemon, is_shiny_setted),
        'typing': data.get_typing(pokemon),
        'emoji1': const.TYPE_EMOJI[data.get_typing_list(pokemon)[0]],
        'emoji2': const.TYPE_EMOJI[data.get_typing_list(pokemon)[1]],
        'abilities': data.get_abilities(pokemon),
        'hidden_ability_line': get_hidden_ability_line(pokemon),
        'evolution_family': data.get_evolution_chain(species),
        'alternative_forms': data.get_alternative_forms(species, pokemon),
        'stats': data.get_stats(pokemon)
    }

    if is_expanded:
        data_dict |= {
            'genus': data.get_english_genus(species.genera),
            'dex_number': data.get_national_dex_number(species),
            'height': data.calculate_height(pokemon.height),
            'weight': data.calculate_weight(pokemon.weight),
            'gender_percentage': data.get_gender_percentage(species),
            'base_friendship': data.get_base_friendship(species),
            'ev_yield': data.get_ev_yield(pokemon),
            'catch_rate': data.get_catch_rate(species),
            'growth_rate': data.get_growth_rate(species),
            'egg_groups': data.get_egg_groups(species),
            'egg_cycles': data.get_egg_cycles(species)
        }
        return script.pokemon_page_expanded.format(**data_dict)

    return script.pokemon_page.format(**data_dict)


def get_hidden_ability_line(pokemon):
    # Additional newlines are added for lines which are not always displayed
    # If they're added, we separate them from the above text
    hidden_ability = data.get_abilities(pokemon, is_hidden=True)
    if not hidden_ability:
        return ''
    return f'\n<b>Hidden ability</b>: {hidden_ability}'
