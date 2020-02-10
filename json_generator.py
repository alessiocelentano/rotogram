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


data[name] = {}


# FORMS
forms_table = soup.find('div', {'class': 'tabs-tab-list'})
forms_list = [i.text for i in forms_table.find_all('a')]


# DEX, TYPING, SPECIES, HEIGHT, WEIGHT AND ABILITIES
forms_data = soup.find_all('div', {'class': 'grid-col span-md-6 span-lg-4'})
del forms_data[0]
for form_data, form in zip(forms_data, forms_list):
    name = re.sub(' ', '_', name.lower())
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
                data[name][form][key][game] = local
        else:
            if ' ' == value.text[-1]:
                value = value.text[:-1]
            else:
                value = value.text
            data[name][form][key] = re.sub('\n', '', value)


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


with open('pkmn.json', 'w') as filee:
    data = json.dump(data, filee, indent=4)
