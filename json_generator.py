#!/usr/bin/python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib.request
import re
import json


with open('pkmn.json', 'r') as filee:
    data = json.load(filee)


user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent': user_agent}
base_url = 'https://pokemondb.net/pokedex/{}'
name = input('Insert Pokémon: ')
url = base_url.format(re.sub(' ', '-', name))
url = re.sub('♀', '-f', url)  # For nidoran
url = re.sub('♂', '-m', url)  # For nidoran
request = urllib.request.Request(url, None, headers)
response = urllib.request.urlopen(request)
dataa = response.read()
soup = BeautifulSoup(dataa, 'html.parser')


name = re.sub(' ', '_', name.lower())
data[name] = {}


# FORMS
forms_table = soup.find('div', {'class': 'tabs-tab-list'})
forms_list = [i.text for i in forms_table.find_all('a')]


# DEX, TYPING, SPECIES, HEIGHT, WEIGHT AND ABILITIES
forms_data = soup.find_all('div', {'class': 'grid-col span-md-6 span-lg-4'})
del forms_data[0]
for form_data, form in zip(forms_data, forms_list):
    form = re.sub(' ', '_', form.lower())
    data[name][form] = {}
    keys_list = form_data.find_all('th')
    for key in keys_list:
        value = key.findNext('td')
        key = re.sub(' ', '', key.text.lower())
        key = re.sub('\u2116', '', key)
        if key == 'abilities':
            data[name][form][key] = {}
            index = 1
            if value.text != '—':  # For Partner Pikachu/Eevee
                for ab in value.span.find_all('a'):
                    data[name][form][key]['ability' + str(index)] = ab.text
                    index += 1
                if value.small:
                    for ab in value.small.find('a'):
                        data[name][form][key]['hidden_ability'] = value.small.a.text
        elif key == 'local':
            data[name][form][key] = {}
            local_list = re.findall('[0-9][0-9][0-9]', value.text)
            for game, local in zip(value.find_all('small'), local_list):
                game = re.sub('[^A-Z0-9]', '', game.text).lower()
                if 'sm' in game or 'usum' in game:
                    # For Alola Dex
                    game = game[:-1]
                if 'xy' in game:
                    # For Kalos Dex
                    game = 'xy'
                elif game == 'lgplge':
                    # LGPE is the correct abbreviation
                    game = 'lgpe'
                elif game == 'p':
                    # Pt is the correct abbreviation
                    game = 'pt'
                elif game == 'ss':
                    # SwSh is the correct abbreviation
                    game = 'swsh'
                data[name][form][key][game] = local
        elif key == 'type':
            value = value.text[1:-1]
            types = re.split(' ', value)
            data[name][form][key] = {}
            data[name][form][key]['type1'] = types[0]
            if len(types) > 1:
                data[name][form][key]['type2'] = types[1]
        elif key == 'height' or key == 'weight':
            values = re.split(' ', value.text)
            data[name][form][key] = {}
            data[name][form][key]['si'] = values[0]
            data[name][form][key]['usc'] = re.sub('[()]', '', values[1])
        else:
            data[name][form][key] = re.sub('\n', '', value.text)


# STATS
stats_list = soup.find_all('div', {'class': 'grid-col span-md-12 span-lg-8'})
key_list = ['hp', 'atk', 'def', 'spa', 'spd', 'spe']
values_list = []
total_list = []
for stats in stats_list:
    if stats == stats_list[-1]:
        pass
    else:
        values_form = [stat.text for stat in stats.find_all('td', {'class': 'cell-num'})]
        values_list.append(values_form)
        total_list.append(stats.find('td', {'class': 'cell-total'}).text)
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
data_list = soup.find_all('div', {'class': 'grid-col span-md-6 span-lg-12'})
index = 0
count = 0
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
            data[name][form][key] = re.split(' ', value.text.replace('\n', ''))[0]
    count += 1


# Evolutions
for form in forms_list:
    form = re.sub(' ', '_', form.lower())
    data[name][form]['evo_methods'] = {'from': None, 'to': None}
    evo_lines_list = soup.find_all('div', {'class': 'infocard-list-evo'})
    split_lines_list = evo_lines_list[0].find_all('div', {'class': 'infocard-list-evo'})
    evo_lines_list = [i for i in evo_lines_list if i not in split_lines_list]
    eevee = ['eevee', 'partner_eevee']
    eeveelutions = [
        'flareon', 'vaporeon', 'jolteon',
        'glaceon', 'leafeon', 'umbreon',
        'espeon', 'sylveon'
    ]
    if name in eeveelutions:
        data[name][name]['preevos'] = ['Eevee']
        data[name][name]['evos'] = {}
        data[name][name]['family'] = eeveelutions
    else:
        for line in evo_lines_list:
            pkmns = line.find_all('div')
            if form in eevee:
                if line == evo_lines_list[0]:
                    family = []
            else:
                family = []
            for pkmn in pkmns:
                infos = pkmn.find('span', {'class': 'infocard-lg-data text-muted'})
                infos_list = infos.find_all('small')
                if len(infos_list) == 3:
                    pkmn_name = infos_list[1]
                    pkmn_name = re.sub(' ', '_', pkmn_name.text.lower())
                else:
                    pkmn_name = infos.find('a').text
                    pkmn_name = re.sub(' ', '_', pkmn_name.lower())
                if pkmn_name not in family:
                    family.append(pkmn_name)
            evo_methods = line.find_all('span', {'class': 'infocard infocard-arrow'})
            for evo_method in evo_methods:
                method_text = re.sub('[()]', '', evo_method.small.text)
                fromm = evo_method.findPrevious('div', {'class': 'infocard'})
                fromm = fromm.find('a', {'class': 'ent-name'}).text
                fromm = re.sub(' ', '_', fromm.lower())
                to = evo_method.findNext('div', {'class': 'infocard'})
                to = to.find('a', {'class': 'ent-name'}).text
                to = re.sub(' ', '_', to.lower())
                if form == fromm:
                    data[name][form]['evo_methods']['from'] = method_text
                if form == to:
                    data[name][form]['evo_methods']['to'] = method_text
            if form not in eevee:
                if form in family:
                    break
        data[name][form]['preevos'] = []
        data[name][form]['evos'] = []
        data[name][form]['family'] = []
        preevo = True
        if form == 'partner_eevee':
            family[0] = form
        if form == 'partner_pikachu':
            family[1] = form
        for i in family:
            if form == i:
                preevo = False
                i = re.sub('_', ' ', i.title())
            else:
                i = re.sub('_', ' ', i.title())
                if preevo:
                    data[name][form]['preevos'].append(i)
                else:
                    data[name][form]['evos'].append(i)
            data[name][form]['family'].append(i)


with open('pkmn.json', 'w') as filee:
    json.dump(data, filee, indent=4)
