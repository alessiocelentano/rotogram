def get_abilities(pkmn_data):
    ability_dict = {"abilities": [], "hidden_ability": None}
    for ability in pkmn_data.abilities:
        if ability.is_hidden:
            ability_dict["hidden_ability"] = ability.name.title()
        else:
            ability_dict["abilities"].append(ability.name.title())
    return ability_dict


def gender_percentage(gender):
    if species.gender_rate = -1:
        gender = "Genderless"
    else:
        female = species.gender_rate / 8 * 100
        male = 100 - female
        gender = f"male: {male}%\nfemale: {female}%"


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
