import requests

def run(data, settings):
    if (data['payload'] == 'michigan fact') or (data['payload'] == 'Michigan fact'):
        r = requests.get('http://api.perreau.lt/michigan_facts/random.json')
        return r.json()['fact']
