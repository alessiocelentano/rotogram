import evolutions
import script
import const


def get_pokemon_full_name(pokemon, species):
    species_full_name = get_english_name(species)

    pokemon_name_elements = pokemon.name.split('-')
    species_name_elements = species.name.split('-')
    form_name_elements = [elem for elem in pokemon_name_elements if elem not in species_name_elements]

    if not form_name_elements:
        return species_full_name

    for form in const.MAIN_ALTERNATIVE_FORMS:
        if form not in form_name_elements:
            continue
        form_name = const.MAIN_ALTERNATIVE_FORMS[form]
        mega_version = f' {form_name_elements[-1]}' if form_name_elements[-1] in ['x', 'y'] else ''
        return f'{form_name} {species_full_name}{mega_version.title()}'

    return f'{species_full_name} ({" ".join(form_name_elements).title()})'


def get_home_thumb_url(pokemon, is_shiny):
    thumb_url = pokemon.sprites.front_default
    if not thumb_url:
        return None
    if is_shiny:
        return thumb_url.replace('pokemon', 'pokemon/other/home/shiny')
    else:
        return thumb_url.replace('pokemon', 'pokemon/other/home')


def get_typing(pokemon):
    typing_list = get_typing_list(pokemon)
    return typing_to_text(typing_list)


def get_typing_list(pokemon):
    typing_list = [t.type.name for t in pokemon.types]
    if len(typing_list) == 1:
        typing_list.append(None)
    return typing_list


def typing_to_text(typing_list):
    return ' / '.join(list(filter(None, typing_list))).title()


def get_abilities(pokemon, is_hidden=False):
    ability_list = get_ability_list(pokemon, is_hidden)
    return abilities_to_text(ability_list)


def get_ability_list(pokemon, is_hidden):
    ability_list = []

    for ability in pokemon.abilities:
        if is_hidden is ability.is_hidden:
            ability_full_name = prettify_name(ability.ability.name)
            ability_list.append(ability_full_name)

    return ability_list


def abilities_to_text(ability_list):
    return " / ".join(ability_list)


def get_evolution_chain(species):
    chain = evolutions.get_chain(species)
    if evolutions.has_evolution(chain):
        evolution_text = evolutions.chain_to_text(chain, species.name)
        return evolution_text
    return script.no_evolutions


def get_alternative_forms(species, pokemon):
    alternative_forms_list = get_alternative_forms_list(species, pokemon)
    return alternative_forms_to_text(alternative_forms_list)


def get_alternative_forms_list(species, pokemon):
    alternative_forms_list = []

    for alternative_form in species.varieties:
        if alternative_form.pokemon.name == pokemon.name:
            continue
        alternative_forms_list.append(alternative_form.pokemon)

    return alternative_forms_list


def alternative_forms_to_text(alternative_forms_list):
    lines = []
    if not alternative_forms_list:
        return ''
    lines.append('\n\n<u><b>Alternative form(s)</b></u>')
    lines.append(', '.join([prettify_name(form.name) for form in alternative_forms_list]))
    return '\n'.join(lines)


def get_stats(pokemon):
    stats_dict = get_stats_dict(pokemon)
    return stats_to_text(stats_dict)


def get_stats_dict(pokemon):
    return {stat.stat.name: stat.base_stat for stat in pokemon.stats}


def stats_to_text(stats_dict):
    lines = []
    for stat_name, stat_value in stats_dict.items():
        lines.append(f'{stat_value} {get_short_stat_name(stat_name)} {get_stats_rating_emoji(stat_value)}')
    return '\n'.join(lines)


def get_short_stat_name(stat):
    if stat == "hp": return "HP"
    if stat == "attack": return "ATK"
    if stat == "defense": return "DEF"
    if stat == "special-attack": return "SPA"
    if stat == "special-defense": return "SPD"
    if stat == "speed": return "SPE"


def get_stats_rating_emoji(stat_value):
    if stat_value < 20: return const.RED_CIRCLE
    if stat_value < 50: return const.ORANGE_CIRCLE * 2
    if stat_value < 80: return const.YELLOW_CIRCLE * 3
    if stat_value < 100: return const.GREEN_CIRCLE * 4
    if stat_value < 130: return const.BLUE_CIRCLE * 5
    else: return const.PURPLE_CIRCLE * 6


def get_national_dex_number(species):
    return species.order


def calculate_height(pokemon_height):
    return f'{pokemon_height / 10} m'


def calculate_weight(pokemon_weight):
    return f'{pokemon_weight / 10} kg'


def get_gender_percentage(species):
    if species.gender_rate == -1:
        return "Genderless"
    else:
        female = species.gender_rate / 8 * 100
        male = 100 - female
        return f"{male}% / {female}%"


def get_base_friendship(species):
    return species.base_happiness


def get_ev_yield(pokemon):
    ev_yield_dict = get_ev_yield_dict(pokemon)
    return ev_yield_to_text(ev_yield_dict)


def get_ev_yield_dict(pokemon):
    return {stat.effort: get_short_stat_name(stat.stat.name) for stat in pokemon.stats if stat.effort != 0}


def ev_yield_to_text(ev_yield_dict):
    return " / ".join([f'{ev_stat} {ev_yield}' for ev_stat, ev_yield in ev_yield_dict.items()])


def get_catch_rate(species):
    return species.capture_rate


def get_growth_rate(species):
    return prettify_name(species.growth_rate.name)


def get_egg_groups(species):
    egg_groups_dict = [prettify_name(group.name) for group in species.egg_groups]
    return egg_groups_to_text(egg_groups_dict)


def egg_groups_to_text(egg_groups_dict):
    return " / ".join(egg_groups_dict)


def get_egg_cycles(species):
    return species.hatch_counter


def get_english_name(species):
    for name in species.names:
        if name.language.name == 'en':
            return name.name


def get_english_genus(genus_name_list):
    for name in genus_name_list:
        if name.language.name == 'en':
            return name.genus


def prettify_name(name):
    name_elements = name.split('-')
    if 'mega' in name_elements:
        name_elements.remove('mega')
        name_elements.insert(0, 'mega')
    if 'gmax' in name_elements:
        name_elements.remove('gmax')
        name_elements.insert(0, 'gigantamax')
    return ' '.join(name_elements).title()
