import re


def add_line(pk, species, chain, text, stage_n):
    for stage in chain:
        name = pk.get_pokemon_species(stage.species.name).names[7].name
        if name == species.names[7].name:
            name = name.join(["<u>", "</u>"])
        if stage_n == 1:
            prefix = ""
        elif stage_n == 2:
            prefix = "↳"
        elif stage_n == 3:
            prefix = "   ↳"
        text += prefix + name + "\n"
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
