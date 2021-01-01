def locations_text(data, pkmn):
    text = ''
    form = list(data[pkmn].keys())[0]
    loc_dict = data[pkmn][form]['location']
    games = []
    locations = []
    for game, location in loc_dict.items():
        game = find_game_name(game)
        if location != 'Trade/migrate from another game':
            if location in locations:
                # Merge games with the same location
                for game2, location2 in zip(games, locations):
                    if location == location2:
                        games[games.index(game2)] += '/' + game
            else:
                # Initialize lists
                games.append(game)
                locations.append(location)

    for game, location in zip(games, locations):
        text += '<b>' + game + '</b>: <i>' + location + '</i>\n'

    return text
