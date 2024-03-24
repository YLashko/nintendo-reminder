from telebot.async_telebot import AsyncTeleBot
from telebot import types
from src.api_handler.handler import APIHandler
from src.bot.user import User
from src.etc.logger import Logger
from src.etc.storage import Storage
from config import packed_parameters, TOKEN
import asyncio
from src.bot.exceptions import BotError, UnexpectedBehavior, UserCancel

class States:
    Idle = 'idle'
    ChooseGame = 'choose_game'

# main class to conntect everything and first layer to handle user requests
class BotHandler:
    def __init__(self, config: dict):
        self.bot = AsyncTeleBot(config['token'])
        self.storage = Storage(config['db_location'])
        self.logger = Logger(self.storage)
        self.api_handler = APIHandler()
        self.users: dict[str, User] = {}
    
    def add_user(self, telegram_id):
        if telegram_id not in self.users.keys():
            self.users[telegram_id] = User(telegram_id)

    def get_user(self, user_id):
        if user_id not in self.users.keys():
            raise BotError('User does not exist')
        return self.users[user_id]
    
    def user_set_region(self, user_id, region):
        self.get_user(user_id)
        if region not in self.api_handler.supported_regions:
            raise BotError('Region is not supported. Supported regions: ' + ', '.join(self.api_handler.supported_regions))
        self.users[user_id].set_region(region)
    
    def get_user_region(self, user_id):
        self.get_user(user_id)
        if self.users[user_id].region == None:
            raise BotError('Region is not set')
        return self.users[user_id].region

    def games_search(self, user_id, search_text):

        def extract_games(generator):
            a = []
            for _ in range(9):
                try:
                    a.append(next(generator))
                except StopIteration:
                    break
            return a

        user = self.get_user(user_id)
        if user.region == None:
            raise BotError('Region is not set')
        
        user.set_state(States.ChooseGame)        
        games_list = extract_games(self.api_handler.search(search_text, user.region))
        return [
            game.title
            for game in games_list
        ]
    
    def choose_game(self, text: str, user: User) -> str:
        user.set_state(States.Idle)
        if user.region == None:
            raise BotError('Region is not set')
        
        game = self.api_handler.get_game(title=text, region=user.region)
        return f'You are now subscribed to {game.title} in {user.region} ({game.nsuid})'
        
    
    def text_message(self, user_id: str, text: str) -> str:
        if user_id not in self.users.keys():
            raise UnexpectedBehavior('Unexpected message')
        user = self.users[user_id]
        if text == 'Cancel':
            user.set_state(States.Idle)
            raise UserCancel('Cancel')
        
        response = 'Unexpected message'
        if user.state == States.ChooseGame:
            response = self.choose_game(text, user)
        
        return response


bot = AsyncTeleBot(TOKEN)
bot_handler = BotHandler(packed_parameters)


@bot.message_handler('start')
async def start_message(message):
    bot_handler.add_user(message.from_user.id)
    await bot.send_message(message.from_user.id, 'Hello!')

@bot.message_handler('region')
async def set_region(message):
    args = message.text.split()
    if len(args) == 2:
        region = args[1]
        try:
            bot_handler.user_set_region(message.from_user.id, region)
            await bot.send_message(message.from_user.id, 'Region set to ' + region)
        except BotError as e:
            await bot.send_message(message.from_user.id, e)
    if len(args) == 1:
        try:
            region = bot_handler.get_user_region(message.from_user.id)
            await bot.send_message(message.from_user.id, 'Your region is ' + region)
        except BotError as e:
            await bot.send_message(message.from_user.id, e)


@bot.message_handler('search')
async def search_games(message):

    def generate_markup(arr, row_length):
        c = 0
        markup = types.ReplyKeyboardMarkup()
        while c < len(arr):
            markup.row(*arr[c : min(len(arr), c + row_length)])
            c += row_length
        return markup

    args = message.text.split()
    if len(args) > 1:
        try:
            games = bot_handler.games_search(message.from_user.id, ' '.join(args[1:]))
            markup = generate_markup(games + ['Cancel'], 2)
            await bot.send_message(message.from_user.id, 'Choose a game to add', reply_markup=markup)
        except BotError as e:
            await bot.send_message(message.from_user.id, e)

@bot.message_handler(func=lambda message: True)
async def handle_text(message):
    try:
        response = bot_handler.text_message(message.from_user.id, message.text)
        await bot.send_message(message.from_user.id, response, reply_markup=types.ReplyKeyboardRemove(selective=False))
    except BotError as e:
        await bot.send_message(message.from_user.id, e)
    except UserCancel:
        await bot.send_message(message.from_user.id, 'Canceled', reply_markup=types.ReplyKeyboardRemove(selective=False))
    except UnexpectedBehavior:
        ...

async def scheduler():
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(bot.infinity_polling())
    asyncio.run(scheduler())
