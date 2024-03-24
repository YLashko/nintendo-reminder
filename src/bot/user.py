# users' data lives here, user preferences, requests and other things
class User:
    def __init__(self, telegram_id: str, region: str = None, state: str = 'idle'):
        self.telegram_id = telegram_id
        self.region = region
        self.state = state

    def set_region(self, region):
        self.region = region
    
    def set_state(self, state):
        self.state = state
