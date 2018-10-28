from .Command import Command


class Ping(Command):
    def __init__(self, slack, bot):
        super().__init__(slack, bot)

        self.cmd = 'ping'

    def run(self, tokens):
        self.slack.respond('pong')
        return
