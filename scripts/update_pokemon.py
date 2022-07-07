import os

import pokepy

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
FILE_PATH = f'{PROJECT_ROOT}/src/pokemon.txt'


def update_pokemon():
    content = ''
    pokemon_id = 1
    while True:
        try:
            content += add_pokemon(pokemon_id)
            pokemon_id += 1
        except Exception:
            print('Operation completed')
            break
    with open(FILE_PATH, 'w') as f:
        f.write(content)


def add_pokemon(pokemon_id):
    text = ''
    species = pokepy.V2Client().get_pokemon_species(pokemon_id).pop()
    text += species.name + '\n'
    print(f'Adding {species.name}')
    return text


if __name__ == '__main__':
    update_pokemon()
