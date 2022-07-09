from client import pokemon_client

from misc import (get_english_genus, get_english_name_of,
                  get_thumb_url, get_formatted_typing)
import script
import const


def get_text(species, pokemon, is_expanded=False, is_shiny=False):
    data = dict()
    data['name'] = get_english_name_of(species)
    data['artwork_link'] = get_thumb_url(pokemon, is_shiny)
    data['types'] = get_formatted_typing(pokemon)
    data['abilities'] = get_formatted_abilities(pokemon)
    data['hidden_ability'] = get_formatted_abilities(pokemon, hidden_ability=True)
    types = [t.type.name for t in pokemon.types]
    data['primary_type'] = types[0]
    data['secondary_type'] = types[1] if len(types) > 1 else 'no'
    data['evolution_family'] = get_formatted_evolution_chain(species)
    data['alternative_forms'] = get_formatted_alternative_forms(species, pokemon)
    data['stats'] = {stat.stat.name: stat.base_stat for stat in pokemon.stats}
    data['stats_rating'] = get_stats_rating_emoji(data['stats'])
    if is_expanded:
        data['genus'] = get_english_genus(species.genera)
        data['dex_number'] = species.order
        data['height'] = str(pokemon.height / 10) + ' m'
        data['weight'] = str(pokemon.weight / 10) + ' kg'
        data['gender_percentage'] = get_gender_percentage(species)
        data['base_friendship'] = species.base_happiness
        ev_yield = {get_short_stat_name(stat.stat.name): stat.effort for stat in pokemon.stats if stat.effort != 0}
        data['ev_yield_text'] = " / ".join([str(ev_yield[stat]) + " " + stat for stat in ev_yield])
        data['catch_rate'] = species.capture_rate
        data['growth_rate'] = species.growth_rate.name.title().replace("-", " ")
        egg_groups = [group.name.title().replace("-", " ") for group in species.egg_groups]
        data['egg_groups_text'] = " / ".join(egg_groups)
        data['egg_cycles'] = species.hatch_counter
    return script.pokemon_page(data, is_expanded)


def get_formatted_abilities(pokemon, hidden_ability=False):
    abilities = get_abilities(pokemon, hidden_ability)
    return ' / '.join(abilities)


def get_abilities(pokemon, hidden_ability=False):
    ability_list = list()
    for ability in pokemon.abilities:
        ability_text = ability.ability.name.title().replace('-', ' ')
        if hidden_ability == ability.is_hidden:
            ability_list.append(ability_text)
    return ability_list


def get_formatted_evolution_chain(species):
    chain = get_chain_obj(species)
    if has_evolution(chain):
        evolution_text = serialize_evolutions(chain, species.name)
        return evolution_text
    return script.no_evolutions


def get_chain_obj(species):
    chain_url = species.evolution_chain.url
    chain_id = chain_url.split('/').pop(-2)
    chain = pokemon_client.get_evolution_chain(chain_id).pop().chain
    return chain


def serialize_evolutions(stage, stage_searched_name, stage_index=1):
    text = ''
    species = pokemon_client.get_pokemon_species(stage.species.name).pop()
    methods = get_evolution_method(stage.evolution_details)
    stage_name = get_english_name_of(species)

    if has_evolution(stage):
        for stage in stage.evolves_to:
            text += serialize_evolutions(stage, stage_searched_name, stage_index=stage_index+1)

    arrow_prefix = add_arrows_scheme(stage_index)
    if species.name == stage_searched_name:
        stage_name = stage_name.join(['<u>', '</u>'])

    return f'{arrow_prefix}{stage_name} {methods}\n{text}'


def has_evolution(species):
    return 'evolves_to' in dir(species) and species.evolves_to


def serialize_pokemon_name(pokemon_name):
    return pokemon_name.replace('-', ' ').title()


def get_evolution_method(method_list):
    method_text_list = list()
    for method in method_list:
        method_text_list.append('{} {}'.format(
            serialize_trigger(method.trigger.name),
            serialize_condition(method)
        ))
    if not method_text_list: return ''
    return '({})'.format(' / '.join(method_text_list))


def serialize_trigger(trigger):
    if trigger == 'level-up': return 'Level'
    if trigger == 'use-item': return 'Use'
    if trigger == 'trade': return 'Trade'
    if trigger == 'shed': return script.shedinja_method
    if trigger == 'spin': return script.alcremie_method
    if trigger == 'tower-of-darkness': return script.urshifu_method
    if trigger == 'tower-of-waters': return script.urshifu_method
    if trigger == 'three-critical-hits': return script.sirfetch_method
    if trigger == 'take-damage': return script.runerigus_method


def serialize_condition(method):
    condition_list = list()
    if method.trigger.name == 'level-up':
        if method.min_level: condition_list.append(str(method.min_level))
        else: condition_list.append('up')
    if method.min_happiness: condition_list.append('with high happiness')
    if method.min_beauty: condition_list.append('with high beauty')
    if method.min_affection: condition_list.append('with high affection')
    if method.needs_overworld_rain: condition_list.append('during rain')
    if method.relative_physical_stats == 1: condition_list.append('if Attack > Defense')
    if method.relative_physical_stats == -1: condition_list.append('if Attack < Defense')
    if method.relative_physical_stats == 0: condition_list.append('if Attack = Defense')
    if method.turn_upside_down: condition_list.append(script.malamar_method)
    if method.time_of_day: condition_list.append('during ' + method.time_of_day.title())
    if method.trade_species: condition_list.append('with ' + method.trade_species.name.title())
    if method.known_move_type: condition_list.append('knowing a {} move'.format(method.known_move_type.name.title()))
    if method.party_type: condition_list.append('with a {} Pokémon in the party'.format(method.party_type.name.title()))
    if method.gender: condition_list.append('[only female]' if method.gender == 1 else '[only male]')
    if method.item:
        item = pokemon_client.get_item(method.item.name).pop()
        condition_list.append(get_english_name_of(item))
    if method.held_item:
        item = pokemon_client.get_item(method.held_item.name).pop()
        condition_list.append('holding ' + get_english_name_of(item))
    if method.known_move:
        move = pokemon_client.get_move(method.held_item.name).pop()
        condition_list.append('knowing ' + get_english_name_of(move))
    if method.location:
        location = pokemon_client.get_location(method.location.name).pop()
        condition_list.append('in ' + get_english_name_of(location))
    if method.party_species:
        species = pokemon_client.get_pokemon_species(method.party_species.name).pop()
        condition_list.append('with {} in the party'.format(species))
    return ' '.join(condition_list)


def add_arrows_scheme(stage_index):
    if stage_index == 1: return ''
    if stage_index == 2: return '↳ '
    if stage_index == 3: return '   ↳ '


def get_formatted_alternative_forms(species, pokemon):
    text = ''
    alternative_forms_dict = get_alternative_forms_dict(species, pokemon)
    if alternative_forms_dict['megaevolution']:
        text += '<b>Megaevolution</b> available\n'
    if alternative_forms_dict['gigantamax']:
        text += '<b>Gigantamax</b> available\n'
    if alternative_forms_dict['other']:
        text += '\n<u><b>Alternative form(s)</b></u>\n'
        text += ', '.join([prettify_form_name(form.name) for form in alternative_forms_dict['other']])
        text += '\n'
    return text


def get_alternative_forms_dict(species, pokemon):
    alternative_forms_dict = {
        'megaevolution': False,
        'gigantamax': False,
        'other': [],
    }
    for alternative_form in species.varieties:
        if alternative_form.pokemon.name == pokemon.name:
            continue
        elif '-mega' in alternative_form.pokemon.name:
            alternative_forms_dict['megaevolution'] = True
        elif '-gmax' in alternative_form.pokemon.name:
            alternative_forms_dict['gigantamax'] = True
        else:
            alternative_forms_dict['other'].append(alternative_form.pokemon)
    return alternative_forms_dict


def prettify_form_name(form_name):
    return form_name.replace('-', ' ').title()


def get_stats_rating_emoji(stats_dict):
    emoji_dict = {}
    for stat in stats_dict:
        stat_value = stats_dict[stat]
        if stat_value < 20: rating_emoji = const.RED_CIRCLE
        elif stat_value < 50: rating_emoji = const.ORANGE_CIRCLE * 2
        elif stat_value < 80: rating_emoji = const.YELLOW_CIRCLE * 3
        elif stat_value < 100: rating_emoji = const.GREEN_CIRCLE * 4
        elif stat_value < 130: rating_emoji = const.BLUE_CIRCLE * 5
        else: rating_emoji = const.PURPLE_CIRCLE * 6
        emoji_dict[stat] = rating_emoji
    return emoji_dict


def get_gender_percentage(species):
    if species.gender_rate == -1:
        return "Genderless"
    else:
        female = species.gender_rate / 8 * 100
        male = 100 - female
        return f"{male}% / {female}%"


def get_short_stat_name(stat):
    if stat == "hp": return "HP"
    if stat == "attack": return "ATK"
    if stat == "defense": return "DEF"
    if stat == "special-attack": return "SPA"
    if stat == "special-defense": return "SPD"
    if stat == "speed": return "SPE"
