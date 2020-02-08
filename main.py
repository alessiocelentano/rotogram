#!/usr/bin/python3
from bs4 import BeautifulSoup
import urllib.request
import re
import json

with open('/home/alessio/Scrivania/dev/Rotomgram/pkmn.json', 'r') as filee:
    datas = json.load(filee)

# ---formal stuff---
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent': user_agent}
base_url = 'https://bulbapedia.bulbagarden.net/wiki/{}_(Pok%C3%A9mon)'
name = re.sub('[\s]', '_', input('Nome Pokemon: ').title())
url = base_url.format(name)
request = urllib.request.Request(url, None, headers)
response = urllib.request.urlopen(request)
data = response.read()
soup = BeautifulSoup(data, 'html.parser')
# ---formal stuff---


table = soup.find('table', {'class': 'roundy'})


# ABILITIES
abilities = [{}]
forms = [name]
parents_list = soup.find_all('td', {'class': 'roundy'})
for parent in parents_list:
    if 'Ability' in parent.a.attrs.values():
        par = parent
        break
abilities_list = par.find_all('td')
form_index = 0
index = 1
for ability in abilities_list:
    if 'display: none' not in ability.attrs.values():
        forms_list = ability.find_all('small')
        for i in forms_list:
            if i.text:
                if 'Hidden Ability' not in i.text and i.text not in forms:
                    forms.append(i.text)
        for i in ability.find_all('a'):
            ab = i.span.text
            if ability.small is None:
                form = 'Ability' + str(index)
                index += 1
                abilities[-1][form] = ab
                continue
            if ability.small.text != forms[form_index]:
                if 'Hidden Ability' not in ability.small.text:
                    abilities.append({})
                    form_index += 1
                    index = 1
                    form = 'Ability' + str(index)
                else:
                    form = 'Hidden Ability'
            else:
                form = 'Ability' + str(index)
                index += 1
            abilities[-1][form] = ab


# TYPE(S) AND FORMS
types = []
type_table = soup.find('table', {'class': 'roundy', 'width': '100%', 'style': 'background: #FFF; padding-top: 3px;'})
types_list = type_table.find_all('table', {'style': 'margin:auto; background:none;'})
forms_list = type_table.find_all('small')
for typee, form in zip(types_list, forms_list):
    index = 0
    a = typee.find_all('a')
    for i in a:
        if i.text != 'Unknown':
            index += 1
    if index == 1:
        types.append([])
        if form.text:
            if form.text not in forms and 'Hidden Ability' not in form.text:
                forms.append(form.text)
        types[-1].append(a[0].text)
    elif index == 2:
        types.append([])
        if form.text:
            if form.text not in forms and 'Hidden Ability' not in form.text:
                forms.append(form.text)
        types[-1].append(a[0].text)
        types[-1].append(a[1].text)


# DEX NUM
dex = table.find('a', {'title': 'List of Pokémon by National Pokédex number'}).span.text


# STATS
stats = []
ref1 = soup.find('span', {'id': 'Base_stats'})
zone1 = ref1.findAllNext('span', {'class': 'mw-headline'})
ref2 = soup.find('span', {'class': 'mw-headline', 'id': 'Pok.C3.A9athlon_stats'})
if not ref2:
    ref2 = soup.find('span', {'class': 'mw-headline', 'id': 'Type_effectiveness'})
zone2 = ref2.findAllPrevious('span', {'class': 'mw-headline'})
forms_list = [elem for elem in zone1 if elem in zone2]
stats_names = ['HP', 'Atk', 'Def', 'SpA', 'SpD', 'Spe', 'Total']
if not forms_list:
    forms_list = ['Base stats']
values = soup.find_all('div', {'style': 'float:right'})
index = 0
for form in forms_list:
    stats.append({})
    for stat in stats_names:
        stats[-1][stat] = values[index].text
        index += 1


# gender_ratio = table.find('title', {'title': 'List of Pokémon by gender ratio'})


datas[name] = {}
index = 0
for form in forms:
    datas[name][form] = {}
    if name in form:
        datas[name][form]['name'] = form
    else:
        datas[name][form]['name'] = name + ' ({})'.format(form)
    datas[name][form]['dex'] = dex
    datas[name][form]['type'] = types[index]
    datas[name][form]['ability'] = {}
    for i, j in zip(abilities[index], abilities[index].values()):
        datas[name][form]['ability'][i] = j
    datas[name][form]['stats'] = {}
    for i, j in zip(stats[index], stats[index].values()):
        datas[name][form]['stats'][i] = j
    index += 1


with open('/home/alessio/Scrivania/dev/Rotomgram/pkmn.json', 'w') as filee:
    json.dump(datas, filee, indent=4)
