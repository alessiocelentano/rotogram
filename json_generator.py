#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import json
import urllib

from bs4 import BeautifulSoup


def find_name(pkmn):
	""" A simply function for find the Pokémon name by HTML snippet (pkmn) """
	if len(pkmn.find_all('small')) == 3:
		pkmn_name = pkmn.find_all('small')[-2].text
	else:
		pkmn_name = pkmn.find_all('a')[1].text
	return pkmn_name


def find_acronym(game):
	game = re.sub('[^A-Z0-9]', '', game.text).lower()
	# Delete the area of Kalos
	# e.g. Central, Coustal and Mountain
	if 'xy' in game:
		game = 'xy'
	# Delete the "Alola dex" part
	elif 'sm' in game or 'usum' in game:
		if game != 'sm' and game != 'usum':
			game = game[:-1]
	# Just edit it in the right acronym
	elif game == 'rb':
		game = 'redblue'
	elif game == 'y':
		game = 'yellow'
	elif game == 'gs':
		game = 'goldsilver'
	elif game == 'c':
		game = 'crystal'
	elif game == 'rs':
		game = 'rubysapphire'
	elif game == 'e':
		game = 'emerald'
	elif game == 'dp':
		game = 'diamondpearl'
	elif game == 'p':
		game = 'platinum'
	elif game == 'lgplge':
		game = 'lgpe'
	elif game == 'ss':
		game = 'swsh'

	return game



with open('pkmn.json', 'r') as filee:
	data = json.load(filee)


# Get Pokémon page HTML
# Credits: PokémonDB (https://pokemondb.net)
headers = {'User-Agent': 'Mozilla/5.0'}
base_url = 'https://pokemondb.net/pokedex/{}'
name = input('Insert Pokémon: ')
url = base_url.format(
	re.sub(' ', '-', name)
)
url = re.sub('♀', '-f', url)  # For Nidoran♀
url = re.sub('♂', '-m', url)  # For Nidoran♂
request = urllib.request.Request(url, None, headers)
response = urllib.request.urlopen(request)
html = response.read()
soup = BeautifulSoup(html, 'html.parser')


# Name
pkmn = re.sub(' ', '_', name.lower())
data[pkmn] = {}


# Forms
form_tab = soup.find(
	'div', {
		'class': 'tabs-tab-list'
	}
)
form_text = form_tab.find_all('a')
form_list = [i.text for i in form_text]
if form_list[0] == pkmn:
	main_form = True
else:
	main_form = False


# Dex, Typing, Species, Height, Weight and abilities
pokedex_data_list = soup.find_all(
	'div', {
		'class': 'grid-col span-md-6 span-lg-4'
	}
)
del pokedex_data_list[0]  # Ads space, no data

for pokedex_data, form in zip(pokedex_data_list, form_list):
	form = re.sub(' ', '_', form.lower())
	data[pkmn][form] = {}
	keys_list = pokedex_data.find_all('th')
	for key in keys_list:
		value = key.findNext('td')
		key = re.sub('[\u2116 ]', '', key.text.lower())

		if key == 'abilities':
			data[pkmn][form][key] = {}
			index = 1  # To number the abilities
			if value.text != '—':  # For Partner Pikachu/Eevee
				ability_list = value.span.find_all('a')
				for ability in ability_list:
					ability = ability.text
					data[pkmn][form][key]['ability' + str(index)] = ability
					index += 1
				if value.small:
					ha = value.small.a.text
					data[pkmn][form][key]['hidden_ability'] = ha

		# Dex number of each region
		elif key == 'local':
			data[pkmn][form][key] = {}
			local_list = re.findall('[0-9][0-9][0-9]', value.text)
			game_list = value.find_all('small')
			for game, local in zip(game_list, local_list):
				game = find_acronym(game)
				data[pkmn][form][key][game] = local

		elif key == 'type':
			value = value.text[1:-1]  # Delete useless characters
			type_list = re.split(' ', value)
			data[pkmn][form][key] = {}
			data[pkmn][form][key]['type1'] = type_list[0]
			if len(type_list) > 1:
				data[pkmn][form][key]['type2'] = type_list[1]

		elif key == 'height' or key == 'weight':
			value = re.split(' ', value.text)
			data[pkmn][form][key] = {}
			data[pkmn][form][key]['si'] = value[0]
			data[pkmn][form][key]['usc'] = re.sub('[()]', '', value[1])

		else:
			value = re.sub('\n', '', value.text)
			data[pkmn][form][key] = value


# Stats
tmp = soup.find_all(
	'div', {
		'id': 'dex-stats'
	}
)
key_list = ['hp', 'atk', 'def', 'spa', 'spd', 'spe']
value_list = []
total_list = []
for i in tmp:
	values = []
	table = i.find_next('table')
	stats_list = table.find_all('tr')

	for stat in stats_list:
		if stat == stats_list[-1]:
			total_list.append(stat.b.text)
		else:
			stat_list = stat.find_all(
				'td', {
					'class': 'cell-num'
				}
			)
			value = [value.text for value in stat_list]
			values.append(value)
	value_list.append(values)

for form, value in zip(form_list, value_list):
	form = re.sub(' ', '_', form).lower()
	stats = key_list.copy()
	data[pkmn][form]['base_stats'] = {}
	data[pkmn][form]['min_stats'] = {}
	data[pkmn][form]['max_stats'] = {}
	while value:
		data[pkmn][form]['base_stats'][stats[0]] = value[0].pop(0)
		data[pkmn][form]['min_stats'][stats[0]] = value[0].pop(0)
		data[pkmn][form]['max_stats'][stats.pop(0)] = value[0].pop(0)
		del value[0]
	data[pkmn][form]['base_stats']['total'] = total_list.pop(0)


# EV yield, cath rate, base friendship, base exp and growth rate
# Egg groups, gender and egg cycles
data_list = soup.find_all(
	'div', {
		'class': 'grid-col span-md-6 span-lg-12'
	}
)
index = 0  # For iterate form_list
count = 0  # For increment index

for dataa in data_list:
	if count == 2:
		index += 1
		count = 0

	line_list = dataa.find_all('tr')
	for line in line_list:
		key = line.find('th').text
		key = re.sub(' ', '_', key.lower())
		value = line.find('td').text
		form = re.sub(' ', '_', form_list[index].lower())
		if key in ['ev_yield', 'egg_groups', 'gender']:
			if '—' not in value:  # For Partner Pikachu/Eevee
				data[pkmn][form][key] = []
				if key != 'gender':
					value = value[1:-1]
				value = re.split(', ', value)
				for stat in value:
					data[pkmn][form][key].append(stat)
		else:
			data[pkmn][form][key] = value
	count += 1


# Evolutions
tmp = soup.find(
	'div', {
		'id': 'dex-evolution'
	}
)
lines = tmp.find_next_siblings(
	'div', {
		'class': 'infocard-list-evo'
	}
)
target_list = []

for line in lines:
	pkmns = line.find_all(
		'div', {
			'class': 'infocard'
		}
	)
	for pkmnn in pkmns:
		pkmn_name = find_name(pkmnn)
		if pkmn_name in form_list:
			if target_list:
				if pkmnn == target_list[-1]:
					target_list[-1] = pkmnn
				elif pkmnn == pkmns[0]:
					target_list = []
			if pkmnn not in target_list:
				next_methods_list = []
				next_pkmns_list = []
				target_list.append(pkmnn)
				form = re.sub(' ', '_', find_name(pkmnn).lower())
				data[pkmn][form]['evo'] = {}
	if len(target_list) == 1:
		target_list[0]
	for target in target_list:
		pre_method = target.find_previous_sibling(
			'span', {
				'class': 'infocard-arrow'
			}
		)
		if pre_method:
			pre_evo = target.find_previous_sibling(
				'div', {
					'class': 'infocard'
				}
			)
			if not pre_evo:
				tmp = line.find(
					'span', {
						'class': 'infocard-evo-split'
					}
				)
				pre_evo = tmp.find_previous_sibling(
					'div', {
						'class': 'infocard'
					}
				)
			pre_method = re.sub('[()]', '', pre_method.small.text)
			pre_evo = find_name(pre_evo)
		else:
			pre_method, pre_evo = None, None
		next_method = target.find_next_sibling(
			'span', {
				'class': 'infocard-arrow'
			}
		)
		if not next_method:
			tmp = target.find_next_sibling()
			if tmp:
				branches = tmp.find_all(
					'div', {
						'class': 'infocard-list-evo'
					}
				)
				for branch in branches:
					next_method = branch.find(
						'span', {
							'class': 'infocard-arrow'
						}
					)
					next_pkmn = branch.find(
						'div', {
							'class': 'infocard'
						}
					)
					next_method = re.sub('[()]', '', next_method.small.text)
					next_pkmn = find_name(next_pkmn)
					next_methods_list.append(next_method)
					next_pkmns_list.append(next_pkmn)
		else:
			next_method = target.find_next(
				'span', {
					'class': 'infocard-arrow'
				}
			)
			next_pkmn = target.find_next(
				'div', {
					'class': 'infocard'
				}
			)
			next_method = re.sub('[()]', '', next_method.small.text)
			next_pkmn = find_name(next_pkmn)
			next_methods_list.append(next_method)
			next_pkmns_list.append(next_pkmn)

		if not next_methods_list:
			next_method = None
		elif len(next_methods_list) == 1:
			next_method = next_methods_list[0]
		else:
			next_method = next_methods_list
		if not next_pkmns_list:
			next_pkmn = None
		elif len(next_pkmns_list) == 1:
			next_pkmn = next_pkmns_list[0]

		else:
			next_pkmn = next_pkmns_list
		target_text = re.sub(' ', '_', find_name(target).lower())
		data[pkmn][target_text]['evo']['from'] = {
			'evo': pre_evo,
			'method': pre_method
		}
		data[pkmn][target_text]['evo']['into'] = {
			'evo': next_pkmn,
			'method': next_method
		}


# Changes
for form in form_list:
	form = re.sub(' ', '_', form.lower())
	data[pkmn][form]['changes'] = []
	changes_list = target.find_next('ul').find_all('li')
	for change in changes_list:
		data[pkmn][form]['changes'].append(change.text)


# Pokédex entries
tmp = soup.find(
	'div', {
		'id': 'dex-flavor'
	}
)
div_list = tmp.find_next_siblings(
	'div', {
		'class': 'resp-scroll'
	}
)

for div in div_list:
	table = div.find('table')
	if table.attrs == {'class': ['vitals-table']}:
		form = div.find_previous('h3')
		if form:
			form = re.sub(' ', '_', form.text.lower())
			if form not in [
				'gigantamax', 'cap_pikachu', 'partner_cap',
				'original_cap', 'sinnoh_cap', 'kalos_cap',
				'hoenn_cap', 'unova_cap', 'alola_cap'
			]:
				data[pkmn][form]['dex_entries'] = {}
				entries_list = table.find_all('tr')
				for entry in entries_list:
					games = entry.find_all('span')
					for game in games:
						game = re.sub('[ \']', '', game.text.lower())
						entry_text = entry.find('td').text
						data[pkmn][form]['dex_entries'][game] = entry_text
	else:
		break


# Location
data[pkmn][pkmn]['location'] = {}
div = soup.find_all(
	'div', {
		'class': 'grid-col span-md-12 span-lg-8'
	}
)[-1]
lines = div.find_all('tr')
for line in lines:
	games_list = line.find_all('span')
	location = line.find('td')
	for game in games_list:
		game = re.sub('[ \']', '', game.text.lower())
		data[pkmn][pkmn]['location'][game] = location.text


# Name in other languages
data[pkmn][pkmn]['other_lang'] = {}
div = soup.find(
	'div', {
		'class': 'grid-col span-md-12 span-lg-6'
	}
)
lines = div.find_all('tr')
for line in lines:
	lang = line.find('th').text.lower()
	translation = line.find('td').text
	data[pkmn][pkmn]['other_lang'][lang] = translation


# Name origin
data[pkmn][pkmn]['name_origin'] = {}
div = soup.find_all(
	'div', {
		'class': 'grid-col span-md-12 span-lg-6'
	}
)[-1]
origin_list = div.find_all('dt')
descrip_list = div.find_all('dd')
for origin, descrip in zip(origin_list, descrip_list):
	origin = origin.text.lower()
	descrip = descrip.text
	data[pkmn][pkmn]['name_origin'][origin] = descrip


# Moveset
data[pkmn][pkmn]['moveset'] = {}
tmp = soup.find('h3', text='Moves learnt by level up')
moveset = tmp.find_next(
	'ul', {
		'class': 'list-nav panel panel-nav'
	}
)
gens = moveset.find_all('li')
if gens:
	gens = [i for i in gens if not i.attrs]
	base_url = 'https://pokemondb.net{}'
else:
	gens = []
for gen in gens:
	href = gen.find('a').attrs['href']
	moves_url = base_url.format(href)
	request = urllib.request.Request(moves_url, None, headers)
	response = urllib.request.urlopen(request)
	dataa = response.read()
	soup = BeautifulSoup(dataa, 'html.parser')
	games_tabs = soup.find_all(
		'a', {
			'class': 'tabs-tab'
		}
	)
	data_tabs = soup.find_all(
		'div', {
			'class': 'tabs-panel'
		}
	)
	for game, dataa in zip(games_tabs, data_tabs):
		game = find_acronym(game)
		lines = dataa.find_all('tr')
		data[pkmn][pkmn]['moveset'][game] = {}
		for line in lines:
			method = line.find_previous('h3')
			if method.text == 'Moves learnt by level up':
				method = 'level_up'
				first_col = 'level'
			elif method.text == 'Egg moves':
				method = 'egg_moves'
				first_col = None
			elif method.text == 'Move Tutor moves':
				method = 'move_tutor'
				first_col = None
			elif method.text == 'Pre-evolution moves':
				method = 'pre_evo_moves'
				first_col = None
			elif method.text == 'Moves learnt by TM':
				method = 'tm'
				first_col = 'number'
			elif method.text == 'Special moves':
				method = 'special_moves'
				first_col = None
			elif method.text == 'Transfer-only moves':
				method = 'transfer_only'
				first_col = None
			elif method.text == 'Moves learnt by TR':
				method = 'tr'
				first_col = 'number'
			elif method.text == 'Moves learnt by HM':
				method = 'hm'
				first_col = 'number'
			cols = line.find_all('td')
			try:
				if first_col:
					number = cols[0].text
					name = cols[1].text
					typee = cols[2].text
					power = cols[4].text
					if power == '\u2014':
						power = None
					accuracy = cols[5].text
					if accuracy == '\u2014':
						accuracy = None
					name_ = re.sub(' ', '_', name.lower())
					try:
						data[pkmn][pkmn]['moveset'][game][method][name_] = {
							first_col: number,
							'name': name,
							'type': typee,
							'power': power,
							'accuracy': accuracy
						}
					except KeyError:
						data[pkmn][pkmn]['moveset'][game][method] = {}
						data[pkmn][pkmn]['moveset'][game][method][name_] = {
							first_col: number,
							'name': name,
							'type': typee,
							'power': power,
							'accuracy': accuracy
						}
				else:
					name = cols[0].text
					typee = cols[1].text
					power = cols[3].text
					accuracy = cols[4].text
					name_ = re.sub(' ', '_', name.lower())
					try:
						data[pkmn][pkmn]['moveset'][game][method] = {
							first_col: number,
							'name': name,
							'type': typee,
							'power': power,
							'accuracy': accuracy
						}
					except KeyError:
						data[pkmn][pkmn]['moveset'][game][method][name_] = {}
						data[pkmn][pkmn]['moveset'][game][method][name_] = {
							first_col: number,
							'name': name,
							'type': typee,
							'power': power,
							'accuracy': accuracy
						}

			except IndexError:
				continue


with open('pkmn.json', 'w') as filee:
	json.dump(data, filee, indent=4)
