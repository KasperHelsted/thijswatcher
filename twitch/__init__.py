import glob
import json
import os
import uuid

from .Streamer import Streamer
from .TwitchAPI import TwitchAPI


class Twitch(TwitchAPI):
    def __init__(self, slack):
        super().__init__()

        self.slack = slack

        self.settings = self.load_config()

        self.channel_folder = 'data/channels'

        self.channels = []

        self.load_channels()

    def load_channels(self):
        for file in glob.glob(f'{self.channel_folder}/*.json'):
            self.start_stream_listener(file)

    def list_channels(self):
        channels = []

        for file in glob.glob(f'{self.channel_folder}/*.json'):
            with open(file, 'r') as f:
                data = self.read_json(f.read())

                if data.get('streamer') is not None:
                    channels.append(f" - {data.get('streamer')}")

        return channels

    def start_stream_listener(self, file):
        channel_thread = Streamer(file, self.slack)
        channel_thread.start()

        self.channels.append(channel_thread)

    def lookup(self, channel):
        return self.get_channel(channel)

    def local_channel_lookup(self, id_):
        for file in glob.glob(f'{self.channel_folder}/*.json'):
            with open(file, 'r') as f:
                data = self.read_json(f.read())

                if str(data['id']) == id_:
                    return file
        return None

    def create_channel(self, channel_data):
        if self.local_channel_lookup(channel_data.get('_id')) is not None:
            return False

        file = f'{self.channel_folder}/{uuid.uuid4().hex}.json'

        with open(file, 'w') as f:
            f.write(self.write_json({
                "id": channel_data.get('_id'),
                "streamer": channel_data.get('display_name'),
                "url": None,
                "game": None,
                "title": None,
                "live": False
            }))

        self.start_stream_listener(file)

        return True

    def delete_channel(self, id_):
        file = self.local_channel_lookup(id_)

        if file is None:
            return False

        for idx, thread in enumerate(self.channels):
            if thread.is_channel(id_):
                thread.kill()
                del self.channels[idx]

                os.remove(file)
                return True
        return False

    @property
    def config_file(self):
        file = os.environ.get('CONFIG_TWITCH', 'twitch')

        return f'data/settings/{file}.json'

    def load_config(self):
        with open(self.config_file, 'r') as f:
            return self.read_json(f.read())

    def save_config(self):
        with open(self.config_file, 'w') as f:
            return f.write(self.settings)

    @staticmethod
    def read_json(str_):
        return json.loads(str_)

    @staticmethod
    def write_json(str_):
        return json.dumps(str_, indent=4)
