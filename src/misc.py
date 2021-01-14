def get_abilities(pkmn_data):
    ability_dict = {"abilities": [], "hidden_ability": None}
    for ability in pkmn_data.abilities:
        if ability.is_hidden:
            ability_dict["hidden_ability"] = ability.ability.name.title().replace("-", " ")
        else:
            ability_dict["abilities"].append(ability.ability.name.title().replace("-", " "))
    return ability_dict


def get_gender_percentage(species):
    if species.gender_rate == -1:
        return "Genderless"
    else:
        female = species.gender_rate / 8 * 100
        male = 100 - female
        return f"male: {male}%\nfemale: {female}%"


def stat_abbr(stat):
    if stat == "hp":
        return "HP"
    if stat == "attack":
        return "ATK"
    if stat == "defense":
        return "DEF"
    if stat == "special-attack":
        return "SPA"
    if stat == "special-defense":
        return "SPD"
    if stat == "speed":
        return "SPE"
