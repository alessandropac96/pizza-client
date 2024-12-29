from typing import MutableMapping
from pizza_client.logger import LogLevels


class LLMClientConfig(MutableMapping):

    defaults = {
        'log_level': LogLevels.INFO,
        'polling_interval': 0.1
    }

    def __init__(self, config):
        self.config = self.fill_missing(config)

    def fill_missing(self, config):
        for key in self.defaults:
            if key not in config:
                config[key] = self.defaults[key]
        return config

    def __getitem__(self, key):
        return self.config[key]

    def __setitem__(self, key, value):
        self.config[key] = value

    def __delitem__(self, key):
        del self.config[key]

    def __iter__(self):
        return iter(self.config)

    def __len__(self):
        return len(self.config)

    def default(self, key):
        return self.defaults[key]