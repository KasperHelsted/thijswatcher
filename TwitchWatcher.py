from slack import Slack


class TwitchWatcher(object):
    def __init__(self):
        self.threads = [
            Slack()
        ]

    def run(self):
        for thread in self.threads:
            thread.start()
