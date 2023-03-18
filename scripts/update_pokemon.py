import os

import pokepy

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
FILE_PATH = f'{PROJECT_ROOT}/src/pokemon.txt'


def main():
    update()


def update(id_=1, content=''):
    # Starting ID is 1 because if new alternative forms are
    # added, we have to iterate again all Pokémons.
    # An infinite loop is used we can't say how many
    # Pokémons there are every new generation
    while True:
        try:
            content += add_pokemon(id_)
            id_ += 1
        except Exception:
            print('Operation completed')
            break

    with open(FILE_PATH, 'w') as f:
        f.write(content)


def add_pokemon(pokemon_id, text=''):
    species = pokepy.V2Client().get_pokemon_species(pokemon_id).pop()
    for variety in species.varieties:
        text += variety.pokemon.name + '\n'
        print(f'Adding {variety.pokemon.name}')
    return text


if __name__ == '__main__':
    main()
