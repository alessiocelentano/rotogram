import re


def get_evolutions_text(evolutions):
    text = ""
    if evolutions["pre_evo"]:
        name = evolutions["pre_evo"]["name"]
        trigger = " / ".join(evolutions["pre_evo"]["trigger"])
        text += f"It evolves from <b>{name}</b> (<i>{trigger}</i>)\n"
    if evolutions["evos"]:
        for i in range(len(evolutions["evos"])):
            name = evolutions["evos"][i]["name"]
            trigger = " / ".join(evolutions["evos"][i]["trigger"])
            if i == 0:
                text += f"It evolves into <b>{name}</b> (<i>{trigger}</i>)"
            elif i == len(evolutions["evos"]) - 1:
                text += f" or into <b>{name}</b> (<i>{trigger}</i>)"
            else:
                text += f", into <b>{name}</b> (<i>{trigger}</i>)"
    return text


def get_chain(pk, species):
    url = species.evolution_chain.url
    chain_id = re.findall("[^v][0-9]+", url)[0]
    chain = [pk.get_evolution_chain(chain_id).chain]
    return chain


def get_evolutions(pk, species):
    evolution_chain = {"pre_evo": {}, "evos": []}
    name = species.names[7].name
    chain = get_chain(pk, species)
    for key in evolution_chain:
        if key == "pre_evo":
            pre_evo_species = species.evolves_from_species
            if pre_evo_species:
                pre_evo = pk.get_pokemon_species(pre_evo_species.name).names[7].name
            else:
                continue
        method_list = []
        while not method_list:
            for stage in chain:
                stage_name = pk.get_pokemon_species(stage.species.name).names[7].name
                if stage_name == name:
                    if key == "pre_evo":
                        method_list = [method.trigger.name.title() for method in stage.evolution_details]
                        evolution_chain["pre_evo"]["name"] = pre_evo
                        evolution_chain["pre_evo"]["trigger"] = method_list
                    else:  # Next stage if it exists
                        try:
                            for next_stage in stage.evolves_to:
                                name = pk.get_pokemon_species(next_stage.species.name).names[7].name
                                method_list = [method.trigger.name.title() for method in next_stage.evolution_details]
                                evolution_chain["evos"].append({"name": name, "trigger": method_list})
                            else:  # stage hasn't evolutions (for Pokemon with only one stage)
                                return evolution_chain
                        except AttributeError:  # stage hasn't evolutions (for sub-stage)
                            return evolution_chain
                    break
            else:
                chain = chain[0].evolves_to
    return evolution_chain
