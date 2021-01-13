import re


def get_method(stage):
    text = ""
    if not stage.evolution_details:
        return ""
    for method in stage.evolution_details:
        if method != stage.evolution_details[0]:
            text += " / "
        if method.trigger.name == "level-up":
            if method.min_level:
                text += "Level " + str(method.min_level)
            else:
                text += "Level up"
        elif method.trigger.name == "use-item":
            text += "Use " + method.item.name.title().replace("-", " ")
        elif method.trigger.name == "trade":
            text += "Trade"
        elif method.trigger.name == "shed":
            text += "Evolve Nincada having one Poké Ball in bag and one empty slot in party"
        elif method.trigger.name == "other":
            if stage.name == "sirfetchd":
                text += "Land three critical hits in one battle"
            if stage.name == "runerigus":
                text += "Travel under the stone bridge in Dusty Bowl after taking at least 49 damage from attacks without fainting"
            if stage.name == "alcremie":
                text += "Spin holding a Sweet"
            if stage.name == "urshifu":
                text += "Interact with Scroll of Darkness/Waters"
        for condition in method.__dict__:
            if method.__dict__[condition] or type(method.__dict__[condition]) == int:
                if condition == "gender":
                    text += " (Female)" if method.__dict__[condition] == 1 else " (Male)"
                elif condition == "held_item":
                    text += " holding " + method.__dict__[condition].names[7].name.replace("-", " ")
                elif condition == "known_move":
                    text += " knowing " + method.__dict__[condition].names[7].name
                elif condition == "known_move_type":
                    text += " knowing a " + method.__dict__[condition].name.title() + " move"
                elif condition == "location":
                    text += " in " + method.__dict__[condition].name.title().replace("-", " ")
                elif condition == "min_happiness":
                    text += " with high happiness"
                elif condition == "min_beauty":
                    text += " with high beauty"
                elif condition == "min_affection":
                    text += " with high affection"
                elif condition == "needs_overworld_rain":
                    text += " during rain"
                elif condition == "min_happiness":
                    text += " with happiness"
                elif condition == "party_species":
                    text += " with " + method.__dict__[condition].names[7].name + " in party"
                elif condition == "party_type":
                    text += " with a " + method.__dict__[condition].names[7].name + "Pokémon in party"
                elif condition == "relative_physical_stats":
                    if method[condition] == 1:
                        relation = ">"
                    elif method[condition] == 1:
                        relation = "<"
                    elif method[condition] == 1:
                        relation = "="
                    text += " if Attack " + relation + "Defense"
                elif condition == "time_of_day":
                    text += " during " + method.__dict__[condition]
                elif condition == "trade_species":
                    text += " with " + method.__dict__[condition].name.title()
                elif condition == "turn_upside_down":
                    text += " turning the console upside down"
    return "(" + text + ")"


def get_prefix(stage_n):
    if stage_n == 1:
        return ""
    elif stage_n == 2:
        return "↳ "
    elif stage_n == 3:
        return "   ↳ "


def add_line(pk, species, chain, text, stage_n):
    for stage in chain:
        name = pk.get_pokemon_species(stage.species.name).names[7].name
        if name == species.names[7].name:
            name = name.join(["<u>", "</u>"])
        prefix = get_prefix(stage_n)
        method = get_method(stage)
        text += f"{prefix}{name} {method}\n"
        try:
            if stage.evolves_to:  # It's empty in base stages
                text = add_line(pk, species, stage.evolves_to, text, stage_n+1)
        except AttributeError:  # It doesn't exist in last stages
            continue
    return text


def get_chain(pk, species):
    url = species.evolution_chain.url
    chain_id = re.findall("[^v][0-9]+", url)[0]
    chain = [pk.get_evolution_chain(chain_id).chain]
    return chain


def get_evolutions(pk, species):
    text = ""
    chain = get_chain(pk, species)
    text = add_line(pk, species, chain, text, 1)
    return text[:-1]
