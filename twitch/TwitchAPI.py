import requests


class TwitchAPI(object):
    def __init__(self):
        self.settings = None

    @property
    def headers(self):
        return {
            'Accept': "application/vnd.twitchtv.v5+json",
            'Client-ID': self.settings.get('client_id')
        }

    def get(self, url):
        return requests.request("GET", url, headers=self.headers)

    def get_channel(self, login):
        return self.get(f'https://api.twitch.tv/kraken/users?login={login}').json()

    def get_channel_by_id(self, id_):
        return self.get(f'https://api.twitch.tv/kraken/channels/{id_}').json()

    def get_channel_info(self, id_):
        return self.get(f'https://api.twitch.tv/kraken/streams/{id_}').json()
