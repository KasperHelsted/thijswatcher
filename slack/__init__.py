import json
import os
import threading
from time import sleep

from slackclient import SlackClient

from twitch import Twitch
from .commands import UseChannel, SetIdentity, TwitchManager, Ping


class Slack(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.running = True

        self.settings = self.load_config()

        self.slack = SlackClient(self.settings.get('chat_token'))
        self.bot = SlackClient(self.settings.get('bot_token'))

        twitch = Twitch(self)

        self.commands = [
            UseChannel(self, self.bot),
            SetIdentity(self, self.bot),
            Ping(self, self.bot),
            TwitchManager(self, self.bot, twitch),
        ]

        self.context = None

        self.announce()

    def announce(self):
        if self.settings.get('first_run', True):
            self.bot.api_call(
                "chat.postMessage",
                channel=self.main_channel(),
                text='Welcome to ThijsWatcher'
            )
            self.settings['first_run'] = False
            self.save_config()

    def main_channel(self, channel=None):
        if channel is not None:
            self.settings['main_channel'] = channel

        if self.settings.get('main_channel') is None:
            self.settings['main_channel'] = self.main_channel(self.get_main_channel())

            if self.settings['main_channel'] is None:
                raise Exception('Could not locate main channel!.')
        return self.settings.get('main_channel')

    def get_main_channel(self):
        for channel in self.slack.api_call("channels.list")['channels']:
            if channel['is_general']:
                return channel['id']
        return None

    def bot_id(self, bot_id=None):
        # <@UDPKWUBHA>
        if bot_id is not None:
            self.settings['bot_id'] = bot_id
        return self.settings.get('bot_id')

    def run(self):
        if self.bot.rtm_connect():
            while self.running:
                for event in self.bot.rtm_read():
                    self.parse_event(event)

                sleep(1)

    def parse_event(self, event):
        if event.get('type') == 'message' and event.get('subtype') != 'bot_message':
            cmd = self.msg_parser(event.get('text'), event)

            if cmd is None:
                return

            for command in self.commands:
                if command.apply(cmd[1]):
                    return command.run(cmd[2:])
            return

    def bot_mentioned(self):
        return f'<@{self.bot_id()}>'

    def msg_parser(self, msg, event):
        self.context = event

        if msg is None:
            return None

        tokens = msg.split(' ')

        if len(tokens) < 2 or (self.bot_mentioned() not in tokens[0] and self.bot_id() is not None):
            return None
        return tokens

    def respond(self, msg):
        return self.send(self.context.get('channel'), msg)

    def send(self, channel=None, msg=None):
        if isinstance(msg, list):
            msg = '\n'.join(msg)

        return self.slack.api_call(
            "chat.postMessage",
            channel=self.main_channel() if channel is None else channel,
            text=msg
        )

    @property
    def config_file(self):
        file = os.environ.get('CONFIG_SLACK', 'slack')

        return f'data/settings/{file}.json'

    def load_config(self):
        with open(self.config_file, 'r') as f:
            return json.loads(f.read())

    def save_config(self):
        with open(self.config_file, 'w') as f:
            return f.write(json.dumps(self.settings, indent=4))
