#!/usr/bin/python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib.request
import re
import json


with open('pkmn.json', 'r') as filee:
    data = json.load(filee)


headers = {'User-Agent': 'Mozilla/5.0'}
base_url = 'https://pokemondb.net/pokedex/{}'
name = input('Insert Pokémon: ')
url = base_url.format(re.sub(' ', '-', name))
url = re.sub('♀', '-f', url)  # For nidoran
url = re.sub('♂', '-m', url)  # For nidoran
request = urllib.request.Request(url, None, headers)
response = urllib.request.urlopen(request)
dataa = response.read()
soup = BeautifulSoup(dataa, 'html.parser')


# NAME
pkmn = re.sub(' ', '_', name.lower())
data[pkmn] = {}


# FORMS
forms_table = soup.find(
    'div', {
        'class': 'tabs-tab-list'
    }
)
forms_list = [i.text for i in forms_table.find_all('a')]


# DEX, TYPING, SPECIES, HEIGHT, WEIGHT AND ABILITIES
pokedex_data_list = soup.find_all(
    'div', {
        'class': 'grid-col span-md-6 span-lg-4'
    }
)
del pokedex_data_list[0]  # Ads space, no data

for pokedex_data, form in zip(pokedex_data_list, forms_list):
    form = re.sub(' ', '_', form.lower())
    data[pkmn][form] = {}
    keys_list = pokedex_data.find_all('th')
    for key in keys_list:
        value = key.findNext('td')
        key = re.sub('[\u2116 ]', '', key.text.lower())

        if key == 'abilities':
            data[pkmn][form][key] = {}
            index = 1  # Number the abilities
            if value.text != '—':  # For Partner Pikachu/Eevee
                for ability in value.span.find_all('a'):
                    ability = ability.text
                    data[pkmn][form][key]['ability' + str(index)] = ability
                    index += 1
                if value.small:
                    for ability in value.small.find('a'):
                        data[pkmn][form][key]['hidden_ability'] = ability
                        # No increment because Hidden Abilities aren't numered

        elif key == 'local':  # Dex number of each region
            data[pkmn][form][key] = {}
            dex_num_list = re.findall('[0-9][0-9][0-9]', value.text)
            for game, num in zip(value.find_all('small'), dex_num_list):
                game = re.sub('[^A-Z0-9]', '', game.text).lower()
                if 'sm' in game or 'usum' in game:
                    game = game[:-1]
                    # Delete the "Alola dex" part
                elif 'xy' in game:
                    game = 'xy'
                    # Delete the part of Kalos
                    # e.g. Central, Coustal and Mountain
                elif game == 'lgplge':
                    game = 'lgpe'
                elif game == 'p':
                    game = 'pt'
                elif game == 'ss':
                    game = 'swsh'
                data[name][form][key][game] = num

        elif key == 'type':
            value = value.text[1:-1]  # Delete useless characters
            types_list = re.split(' ', value)
            data[name][form][key] = {}
            data[name][form][key]['type1'] = types_list[0]
            if len(types_list) > 1:
                data[name][form][key]['type2'] = types_list[1]

        elif key == 'height' or key == 'weight':
            values = re.split(' ', value.text)
            data[name][form][key] = {}
            data[name][form][key]['si'] = values[0]
            data[name][form][key]['usc'] = re.sub('[()]', '', values[1])

        else:
            data[name][form][key] = re.sub('\n', '', value.text)


# STATS
all_stats = soup.find_all(
    'div', {
        'class': 'grid-col span-md-12 span-lg-8'
    }
)
key_list = ['hp', 'atk', 'def', 'spa', 'spd', 'spe']
values_list = []
total_list = []  # Sum of the 6 stats
for stats in all_stats:
    if stats != all_stats[-1]:  # The last one element is the position
        stats_list = stats.find_all(
            'td', {
                'class': 'cell-num'
            }
        )
        values = [value.text for value in stats_list]
        values_list.append(values)
        total_list.append(
            stats.find(
                'td', {
                    'class': 'cell-total'
                }
            ).text
        )
for form in forms_list:
    form = re.sub(' ', '_', form).lower()
    data[name][form]['base_stats'] = {}
    data[name][form]['min_stats'] = {}
    data[name][form]['max_stats'] = {}
    stats = key_list.copy()
    while values_list[0]:
        data[name][form]['base_stats'][stats[0]] = values_list[0].pop(0)
        data[name][form]['min_stats'][stats[0]] = values_list[0].pop(0)
        data[name][form]['max_stats'][stats.pop(0)] = values_list[0].pop(0)
    del values_list[0]
    data[name][form]['base_stats']['total'] = total_list.pop(0)


# EV yield, cath rate, base friendship, base exp and growth rate
# Egg groups, gender and egg cycles
data_list = soup.find_all(
    'div', {
        'class': 'grid-col span-md-6 span-lg-12'
    }
)
index = 0  # For iterate forms_list
count = 0  # For increment index
for i in data_list:
    if count == 2:
        index += 1
        count = 0
    key_list = i.find_all('th')
    value_list = i.find_all('td')
    for key, value in zip(key_list, value_list):
        form = re.sub(' ', '_', forms_list[index].lower())
        key = re.sub(' ', '_', key.text.lower()).replace('.', '')
        if key in ['ev_yield', 'growth_rate', 'egg_groups']:
            if key == 'growth_rate':
                data[name][form][key] = value.text
            else:
                if '—' not in value.text:  # For Partner Pikachu/Eevee
                    data[name][form][key] = []
                    for stat in re.split(', ', value.text[1:-1]):
                        data[name][form][key].append(stat)
        elif key == 'gender':
            data[name][form][key] = value.text
        else:
            value = value.text.replace('\n', '')
            data[name][form][key] = re.split(' ', value)[0]
    count += 1


# Evolutions
for form in forms_list:
    form = re.sub(' ', '_', form.lower())
    data[name][form]['evo_methods'] = {}
    evo_lines_list = soup.find_all(
        'div', {
            'class': 'infocard-list-evo'
        }
    )
    split_evo_list = evo_lines_list[0].find_all(
        'div', {
            'class': 'infocard-list-evo'
        }
    )
    # split_evo_list points the mons that have multiple evolutions
    # Its elements are evo_lines_list children
    # So to avoid useless iterations they will delete in the following line
    evo_lines_list = [i for i in evo_lines_list if i not in split_evo_list]
    for line in evo_lines_list:
        pkmn_list = line.find_all(
            name='div',
            attrs={'class': 'infocard'}
        )
        split = line.find(
            name='span',
            attrs={'class': 'infocard-evo-split'}
        )
        for infocard in pkmn_list:
            if len(infocard.find_all('small')) == 3:
                pkmn_name = infocard.find_all('small')[-2].text
            else:
                pkmn_name = infocard.find_all('a')[1].text
            pkmn_name = re.sub(' ', '_', pkmn_name.lower())
            if pkmn_name == pkmn:
                break
            else:
                continue
        if str(infocard) not in str(split):
            pre_evo = infocard.find_previous_sibling('div')
            if len(pre_evo.find_all('small')) == 3:
                pre_evo_text = pre_evo.find_all('small')[-2].text
            else:
                pre_evo_text = pre_evo.find_all('a')[1].text
            pre_evo_method = infocard.find_previous_sibling('span')
            pre_evo_method_text = re.sub('[()]', '', pre_evo_method.small.text)
            next_span = infocard.find_next_sibling('span')
            if next_span.attrs == {'class':['infocard', 'infocard-arrow']}:
                evo = infocard.find_next_sibling('div')
                if len(evo.find_all('small')) == 3:
                    evo_text = evo.find_all('small')[-2].text
                else:
                    evo_text = evo.find('a').text
                evo_method = infocard.find_next_sibling('span')
                evo_method_text = re.sub('[()]', '', evo_method.small.text)
                data[pkmn][form]['evo_methods'] = {
                    'from': {
                        'name': pre_evo_text,
                        'method': pre_evo_method_text
                    },
                    'into': {
                        'name': evo_text,
                        'method': evo_method_text
                    }
                }
            else:
                evo_list, method_list = [], []
                for split_line in split:
                    evo = split_line.find(
                        'div', {
                            'class': 'infocard'
                        }
                    )
                    if len(evo.find_all('small')) == 3:
                        evo_text = evo.find_all('small')[-2].text
                    else:
                        evo_text = evo.find_all('a')[1].text
                    evo_method = split_line.find(
                        'span', {
                            'class': ['infocard', 'infocard-arrow']
                        }
                    )
                    evo_method_text = re.sub('[()]', '', evo_method.small.text)
                    evo_list.append(evo_text)
                    method_list.append(evo_method_text)
                data[pkmn][form]['evo_methods'] = {
                    'from': {
                        'name': pre_evo_text,
                        'method': pre_evo_method_text
                    },
                    'into': {
                        'name': evo_list,
                        'method': method_list
                    }
                }


with open('pkmn.json', 'w') as filee:
    json.dump(data, filee, indent=4)
