import json
import os
import threading
from copy import deepcopy
from time import sleep

from .TwitchAPI import TwitchAPI


class Streamer(threading.Thread, TwitchAPI):
    def __init__(self, file, slack):
        super().__init__()

        self.file = file
        self.settings = self.load_config(self.config_file)
        self.status = self.load_config(self.file)

        self.msg = []

        self.slack = slack

        self.running = True

        self.init()

    def init(self):
        if self.status.get('streamer') is None:
            streamer_data = self.get_channel_by_id(self.status.get('id'))
            self.status['streamer'] = streamer_data.get('display_name')
            self.status['url'] = streamer_data.get('url')
            self.save_state()

        return

    @property
    def config_file(self):
        file = os.environ.get('CONFIG_TWITCH', 'twitch')

        return f'data/settings/{file}.json'

    @staticmethod
    def load_config(file):
        with open(file, 'r') as f:
            return json.loads(f.read())

    def save_state(self):
        with open(self.file, 'w') as f:
            f.write(json.dumps(self.status, indent=4))

    def is_channel(self, id_):
        return self.status.get('id') == str(id_)

    def kill(self):
        print(f"Killing {self.status.get('streamer')} thread.")
        self.running = False

    def run(self):
        while self.running:
            self.msg = []

            data = self.get_channel_info(self.status.get('id'))

            stream_info = data['stream']

            tmp_status = deepcopy(self.status)

            if stream_info is None or stream_info['stream_type'] == "rerun":
                self.status['game'] = None
                self.status['title'] = None
                self.status['live'] = False
            else:
                streamer = data['stream']['channel']

                self.status['streamer'] = streamer['display_name']
                self.status['url'] = streamer['url']
                self.status['game'] = streamer['game']
                self.status['title'] = streamer['status']
                self.status['live'] = True

            if self.status != tmp_status:
                if self.status['live']:
                    if not tmp_status['live']:
                        self.msg.append(f"{self.status['streamer']} just went live playing {self.status['game']}.")
                        self.msg.append(self.status['title'])
                    elif tmp_status['game'] != self.status['game']:
                        self.msg.append(f"{self.status['streamer']} just started to play {self.status['game']}.")
                    elif tmp_status['title'] != self.status['title']:
                        self.msg.append(f"{self.status['streamer']} just changed the title to {self.status['title']}.")

                    self.msg.append(f"Watch here: {self.status['url']}")
                else:
                    self.msg.append(f"{self.status['streamer']} went offline.")

            self.slack.send(msg=self.msg)
            self.save_state()

            sleep(self.settings.get('sleep'))
