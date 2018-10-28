from .Command import Command


class UseChannel(Command):
    def __init__(self, slack, bot):
        super().__init__(slack, bot)

        self.cmd = 'join'

    def run(self, tokens):
        channel_info = self.channel_regex.search(tokens[0])

        if channel_info is None:
            return None

        channel = self.slack.send(channel_info.group(1), 'I will mainly be communicating here from now on.')

        if not channel.get('ok'):
            self.slack.respond(f'I am not able to write in {tokens[0]}.')
        else:
            self.slack.main_channel(channel_info.group(1))
            self.slack.save_config()
