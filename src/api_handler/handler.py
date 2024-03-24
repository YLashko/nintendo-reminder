from nintendeals import noe, noa
from src.bot.exceptions import BotError

# an api interface to easily translate user request to api responses and handle preferences like country etc
class APIHandler:
    def __init__(self):
        self.supported_regions = set(['pl', 'us'])
        self.regions = {
            'pl': noe,
            'us': noa
        }

    def search(self, query, region):
        if region not in self.supported_regions:
            raise BotError('Unknown region')
        return self.regions[region].search_switch_games(query=query)
    
    def get_game(self, title, region):
        game_generator = self.search(title, region)

        try:
            return next(game_generator)
        except StopIteration:
            raise BotError('Game does not exist')
        