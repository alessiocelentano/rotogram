from pokepy import V2Client as pokemon_client

import const
import data


def get_chain(species):
    chain_url = species.evolution_chain.url
    chain_id = chain_url.split('/').pop(-2)
    chain = pokemon_client().get_evolution_chain(chain_id).pop().chain
    return chain


def chain_to_text(stage, searched_stage_name, stage_index=1):
    lines = []

    if has_evolution(stage):
        for next_stage in stage.evolves_to:
            lines.append(chain_to_text(next_stage, searched_stage_name, stage_index=stage_index+1))

    # species_full_name is used in the evolution "tree" text
    species = pokemon_client().get_pokemon_species(stage.species.name).pop()
    species_full_name = data.get_english_name(species.names)

    if species.name == searched_stage_name:
        # when Pokémon is underlines, we don't need to add the link
        # we are already on the Pokémon page
        species_full_name = species_full_name.join(['<u>', '</u>'])
    else:
        # default_pokemon is used for the link
        # (we have to specify a Pokémon, not a species)
        default_pokemon_name = species.varieties[0].pokemon.name
        default_pokemon = pokemon_client().get_pokemon(default_pokemon_name).pop()

        species_full_name = data.add_pokemon_link(default_pokemon, species_full_name)

    arrow_prefix = get_arrows_prefix(stage_index)
    methods = get_evolution_method(stage.evolution_details)

    return '\n'.join([f'{arrow_prefix}{species_full_name} {methods}'] + lines)


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
    if trigger == 'shed': return const.SHEDINJA_METHOD
    if trigger == 'spin': return const.ALCREMIE_METHOD
    if trigger == 'tower-of-darkness': return const.URSHIFU_METHOD
    if trigger == 'tower-of-waters': return const.URSHIFU_METHOD
    if trigger == 'three-critical-hits': return const.SIRFETCH_METHOD
    if trigger == 'take-damage': return const.RUNERIGUS_METHOD


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
        condition_list.append(const.MALAMAR_METHOD)
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
        condition_list.append(data.get_english_name(item.names))
    if method.held_item:
        item = pokemon_client().get_item(method.held_item.name).pop()
        condition_list.append(f'holding {data.get_english_name(item.names)}')
    if method.known_move:
        move = pokemon_client().get_move(method.held_item.name).pop()
        condition_list.append(f'knowing {data.get_english_name(move.names)}')
    if method.location:
        location = pokemon_client().get_location(method.location.name).pop()
        condition_list.append(f'in {data.get_english_name(location.names)}')
    if method.party_species:
        species = pokemon_client().get_pokemon_species(method.party_species.name).pop()
        condition_list.append(f'with {species} in the party')
    return ' '.join(condition_list)


def get_arrows_prefix(stage_index):
    if stage_index == 1: return ''
    if stage_index == 2: return '↳ '
    if stage_index == 3: return '   ↳ '
