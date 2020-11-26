def get_abilities(pkmn_data):
    ability_dict = {"abilities": [], "hidden_ability": None}
    for ability in pkmn_data.abilities:
        if ability.is_hidden:
            ability_dict["hidden_ability"] = ability.name.title()
        else:
            ability_dict["abilities"].append(ability.name.title())
    return ability_dict
