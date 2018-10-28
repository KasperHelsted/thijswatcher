from .Command import Command


class SetIdentity(Command):
    def __init__(self, slack, bot):
        super().__init__(slack, bot)

        self.cmd = 'identity'

    def run(self, tokens):
        user = self.user_regex.search(tokens[0])

        if user is None:
            return None

        self.bot.api_call(
            "chat.postMessage",
            channel=self.slack.main_channel(),
            text='I finally know who i am :open_mouth:'
        )

        self.slack.bot_id(user.group(1))
        self.slack.save_config()
