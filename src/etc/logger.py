# for easy logging, to convert log requests to text containing system status and logs
class Logger:
    templates = {}

    def __init__(self, storage):
        self.storage = storage
