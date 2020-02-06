from bs4 import BeautifulSoup
import urllib.request

# ---formal stuff---
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent': user_agent}
base_url = 'https://bulbapedia.bulbagarden.net/wiki/{}_(Pok%C3%A9mon)'
url = base_url.format(input('Nome Pokémon: '))
request = urllib.request.Request(url, None, headers)
response = urllib.request.urlopen(request)
data = response.read()
soup = BeautifulSoup(data, 'html.parser')
# ---formal stuff---

# STATS
stats = soup.find_all('div', {'style': 'float:right'})
for stat in stats:
    print(stat.text)

# ABILITIES
parents_list = soup.find_all('td', {'class': 'roundy', 'colspan': '2'})
parent = ''
for i in parents_list:
    try:
        if 'Abilities' in i.contents[1].text:
            parent = i
            break
    except IndexError:
        continue
if not parent:  # 1 ability
    # try again, but search "Ability"
    parents_list = soup.find_all('td', {'class': 'roundy', 'colspan': '2'})
    if parents_list == []:
        parents_list = soup.find_all('td', {'class': 'roundy', 'width': '50%'})
    for i in parents_list:
        if 'Ability' in i.contents[1].text:
            parent = i
            break
    abilities = parent.find_all('td', {'style': 'padding-top:3px; padding-bottom:3px'})
    # for pkmn like Necrozma
    abilities.append(parent.find_all('td', {'colspan': '10'})[0])
else:
    abilities = parent.find_all('td', {'style': ''})

for ability in abilities:
    try:  # 2+ abilities
        form = ability.contents[3].text
        ab = ability.contents[1].text
        print(form + ': ' + ab)
    except IndexError:  # 1/2 abilities
        form = 'Ability'
        ab = ability.contents[1].text
        print(form + ': ' + ab)
