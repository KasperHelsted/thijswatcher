import re


class Command(object):
    def __init__(self, slack, bot):
        self.channel_regex = re.compile(r'<#([A-Z0-9]*)\|(.+)>')
        self.user_regex = re.compile(r'<@([A-Z0-9]*)>')

        self.slack = slack
        self.bot = bot

        self.cmd = ''

    def apply(self, cmd):
        return self.cmp(self.cmd, cmd)

    def run(self, tokens):
        return

    @staticmethod
    def cmp(val1, val2):
        return val1.lower() == val2.lower()
