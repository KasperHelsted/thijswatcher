from .Command import Command


class TwitchManager(Command):
    def __init__(self, slack, bot, twitch):
        super().__init__(slack, bot)

        self.twitch = twitch

        self.cmd = 'twitch'

        self.commands = {
            'add': self.add,
            'remove': self.remove,
            'list': self.list
        }

    def get_channel(self, channel):
        channel_info = self.twitch.lookup(channel)

        if channel_info.get('_total') != 1:
            self.slack.respond(f'I was unable to find {channel} :cry:')
            return None
        return channel_info['users'][0]

    def add(self, channel):
        channel = self.get_channel(channel)

        if channel is None:
            return

        if self.twitch.create_channel(channel):
            self.slack.respond(f':tada: I have now added {channel.get("display_name")} :tada:')
        else:
            self.slack.respond(f'I was not able to add {channel.get("display_name")} :cry:')

    def remove(self, channel):
        channel = self.get_channel(channel)

        if channel is None:
            return

        if self.twitch.delete_channel(channel.get('_id')):
            self.slack.respond(f':tada: I am no longer looking for updates from  {channel.get("display_name")} :tada:')
        else:
            self.slack.respond(f'I was not able to remove {channel.get("display_name")} :cry:')

    def list(self, search):
        channels = self.twitch.list_channels()

        channels.insert(0, "We are following updates from:")

        self.slack.respond(channels)
        return

    def run(self, tokens):
        if len(tokens) < 2:
            return None

        for command, func_ in self.commands.items():
            if self.cmp(command, tokens[0]):
                func_(tokens[1])

        return
