from pokepy import V2Client as pokemon_client

import data
import script


def get_chain(species):
    chain_url = species.evolution_chain.url
    chain_id = chain_url.split('/').pop(-2)
    chain = pokemon_client().get_evolution_chain(chain_id).pop().chain
    return chain


def chain_to_text(stage, searched_stage_name, stage_index=1):
    species = pokemon_client().get_pokemon_species(stage.species.name).pop()
    methods = get_evolution_method(stage.evolution_details)
    stage_name = data.get_english_name(species)
    lines = []

    if has_evolution(stage):
        for stage in stage.evolves_to:
            lines.append(chain_to_text(stage, searched_stage_name, stage_index=stage_index+1))

    arrow_prefix = get_arrows_prefix(stage_index)
    if species.name == searched_stage_name:
        stage_name = stage_name.join(['<u>', '</u>'])

    return '\n'.join([f'{arrow_prefix}{stage_name} {methods}'] + lines)


def has_evolution(species):
    return 'evolves_to' in dir(species) and species.evolves_to


def get_evolution_method(evolution_details):
    method_list = get_evolution_method_list(evolution_details)
    return evolution_to_text(method_list)


def get_evolution_method_list(evolution_details):
    method_list = []
    for method in evolution_details:
        method_list.append('{} {}'.format(
            trigger_to_text(method.trigger.name),
            condition_to_text(method)
        ))
    return method_list


def evolution_to_text(method_list):
    if not method_list:
        return ''
    return '({})'.format(' / '.join(method_list))


def trigger_to_text(trigger):
    if trigger == 'level-up': return 'Level'
    if trigger == 'use-item': return 'Use'
    if trigger == 'trade': return 'Trade'
    if trigger == 'shed': return script.shedinja_method
    if trigger == 'spin': return script.alcremie_method
    if trigger == 'tower-of-darkness': return script.urshifu_method
    if trigger == 'tower-of-waters': return script.urshifu_method
    if trigger == 'three-critical-hits': return script.sirfetch_method
    if trigger == 'take-damage': return script.runerigus_method


def condition_to_text(method):
    condition_list = []
    if method.trigger.name == 'level-up':
        level_suffix = method.min_level if method.min_level else 'up'
        condition_list.append(str(level_suffix))
    if method.min_happiness:
        condition_list.append('with high happiness')
    if method.min_beauty:
        condition_list.append('with high beauty')
    if method.min_affection:
        condition_list.append('with high affection')
    if method.needs_overworld_rain:
        condition_list.append('during rain')
    if method.relative_physical_stats == 1:
        condition_list.append('if Attack > Defense')
    if method.relative_physical_stats == -1:
        condition_list.append('if Attack < Defense')
    if method.relative_physical_stats == 0:
        condition_list.append('if Attack = Defense')
    if method.turn_upside_down:
        condition_list.append(script.malamar_method)
    if method.time_of_day:
        time_of_day = data.prettify_name(method.time_of_day)
        condition_list.append(f'during {time_of_day}')
    if method.trade_species:
        trade_species = data.prettify_name(method.trade_species.name)
        condition_list.append(f'with {trade_species}')
    if method.known_move_type:
        known_move_type = data.prettify_name(method.known_move_type.name)
        condition_list.append(f'knowing a {known_move_type} move')
    if method.party_type:
        party_type = data.prettify_name(method.party_type.name)
        condition_list.append(f'with a {party_type} Pokémon in the party')
    if method.gender:
        gender_only = '[only female]' if method.gender == 1 else '[only male]'
        condition_list.append(gender_only)
    if method.item:
        item = pokemon_client().get_item(method.item.name).pop()
        condition_list.append(data.get_english_name(item))
    if method.held_item:
        item = pokemon_client().get_item(method.held_item.name).pop()
        condition_list.append(f'holding {data.get_english_name(item)}')
    if method.known_move:
        move = pokemon_client().get_move(method.held_item.name).pop()
        condition_list.append(f'knowing {data.get_english_name(move)}')
    if method.location:
        location = pokemon_client().get_location(method.location.name).pop()
        condition_list.append(f'in {data.get_english_name(location)}')
    if method.party_species:
        species = pokemon_client().get_pokemon_species(method.party_species.name).pop()
        condition_list.append(f'with {species} in the party')
    return ' '.join(condition_list)


def get_arrows_prefix(stage_index):
    if stage_index == 1: return ''
    if stage_index == 2: return '↳ '
    if stage_index == 3: return '   ↳ '
