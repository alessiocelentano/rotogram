def get_evo_text(evolutions):
    text = ""
    if evolutions["pre_evo"]:
        name = evolutions["pre_evo"]["name"]
        trigger = " / ".join(evolutions["pre_evo"]["trigger"])
        text += f"It evolves from <b>{name}</b> (<i>trigger</i>)\n"
    if evolutions["evo"]:
        for i in range(len(evolutions["evo"])):
            if i == 1:
                text += f"It evolves into <b>{name}</b> (<i>trigger</i>)"
            elif i == len(evolution["evo"]):
                text += f" or into <b>{name}</b> (<i>trigger</i>)"
            else:
                text += f", into <b>{name}</b> (<i>trigger</i>)"
        text += "\n"
    return text


def get_chain(species):
    url = species.evolution_chain.url
    chain_id = re.findall("[0-9]{3}", url)[0]
    chain = list(pk.get_evolution_chain(chain_id).chain)
    return chain


def get_evo(species, evolution_chain):
    chain = get_chain(species)
    while not method_list:
        for stage in chain:
            if stage.species.name == pkmn:
                name = stage.evolves_to.species.name.title()
                method_list = [method.trigger.name.title() for method in stage.evolves_to.evolution_details]
                evolution_chain["evos"].append({"name": name, "trigger": method_list})
                break
        else:
            chain = chain.evolves_to
    return evolution_chain


def get_pre_evo(speciesm evolution_chain):
    pre_evo_species = species.evolves_from_species
    if pre_evo_species:
        name = pre_evo_species.name.title()
        chain = list(get_chain(species))
        while not method_list:
            for stage in chain:
                if stage.species.name == pkmn:
                    method_list = [method.trigger.name.title() for method in stage.evolution_details]
                    evolution_chain["pre_evo"]["name"] = name
                    evolution_chain["pre_evo"]["trigger"] = method_list
            else:
                chain = chain.evolves_to
        return evolution_chain


def get_evolutions(species):
    evolution_chain = {
        "pre_evo": {},
        "evos": []
    }
    evolution_chain = get_pre_evo(species, evolution_chain)
    evolution_chain = get_evo(species, evolution_chain)
    return evolution_chain
