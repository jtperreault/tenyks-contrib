import requests

from tenyksclient.client import Client, run_client
from tenyksclient.config import settings


SEARCH_URL_TEMPLATE = 'http://autocomplete.wunderground.com/aq?query={location}'
CURRENT_COND_TEMPLATE = 'http://api.wunderground.com/api/{api_key}/conditions{query}.json'
ALERTS_TEMPLATE = 'http://api.wunderground.com/api/{api_key}/alerts{query}.json'

TYPE_CURRENT = 'current'
TYPE_ALERTS = 'alerts'


class TenyksWeather(Client):

    irc_message_filters = {
        'current_weather': r'current weather (.*)',
        'weather_alerts': r'weather alerts (.*)',
    }
    direct_only = True

    def fetch_location(self, location_query):
        search = requests.get(SEARCH_URL_TEMPLATE.format(location=location_query))
        search_json = search.json()
        if search_json['RESULTS']:
            return search_json['RESULTS'][0]['l']
        return None

    def fetch_weather_data(self, data_type, location_string):
        if data_type == TYPE_CURRENT:
            data = requests.get(CURRENT_COND_TEMPLATE.format(
                api_key=settings.WUNDERGROUND_API_KEY,
                query=location_string))
        elif data_type == TYPE_ALERTS:
            data = requests.get(ALERTS_TEMPLATE.format(
                api_key=settings.WUNDERGROUND_API_KEY,
                query=location_string))
        if data.status_code == 200:
            return data.json()

    def handle_current_weather(self, data, match):
        location = match.groups()[0]
        location_string = self.fetch_location(location)
        if location_string:
            current_json = self.fetch_weather_data(TYPE_CURRENT, location_string)
            if current_json:
                template = '{city} is {temp_f}F ({temp_c}C) and {weather}'
                self.send(template.format(
                    city=current_json['current_observation']['display_location']['full'],
                    temp_f=current_json['current_observation']['temp_f'],
                    temp_c=current_json['current_observation']['temp_c'],
                    weather=current_json['current_observation']['weather']), data)
        else:
            self.send('Unknown location', data)

    def handle_weather_alerts(self, data, match):
        location = match.groups()[0]
        location_string = self.fetch_location(location)
        if location_string:
            alerts_json = self.fetch_weather_data(TYPE_ALERTS, location_string)
            if alerts_json and alerts_json['alerts']:
                top_alert = alerts_json['alerts'][0]
                print top_alert
                template = '{advisory} - {message}'
                self.send(template.format(
                    advisory=top_alert['description'],
                    message=top_alert['message'][0:600].replace('\n', '')), data)
            else:
                self.send('No alerts.', data)
        else:
            self.send('Unknown location', data)


def main():
    run_client(TenyksWeather)


if __name__ == '__main__':
    main()
