from .worker import Worker
from aiogram import Bot, Dispatcher, types, Router
# from asyncio import sleep, ensure_future, create_task
# from .statistic_bot import StatisticBot
# from .trading_bot import TradingBot
# from epure.files import IniFile
from aiogram.filters.command import Command, CommandStart
from aiogram.filters import IS_MEMBER, IS_NOT_MEMBER, ChatMemberUpdatedFilter, JOIN_TRANSITION
from argparse import ArgumentParser
from aiogram.enums.chat_type import ChatType
from aiogram.types import ChatMemberUpdated
from ..roles.user import User
from ..migrations.marat1 import migration
from aiogram.types.user import User as TgUser
from ..token.currency import Currency
import traceback
from ..token.wallet import Wallet


class TelegramBot(Worker):
    bot_token:str
    bot:Bot
    dsp:Dispatcher
    config:object

    

    def __init__(self, config:object):        

        self.bot_token = config.bot_token
        self.config = config
        self.bot = Bot(self.bot_token)        
        self.dsp = Dispatcher()
        # self.dsp.message(self.init_user_chat, commands=['start'])           
        self.dsp.message()(self.message_handler)        
        self.dsp.message(CommandStart())(self.init_user_chat)

        router = Router()
        
        self.dsp.chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))(self.new_member)
        print('running')
        # self.dsp.register_message_handler(self.trade, commands=['trade'])
        # self.dsp.register_message_handler(self.stats, commands=['stats'])
        # self.dsp.register_message_handler(self.stop, commands=['stop'])
        # self.dsp.register_message_handler(self.message_handler)        
  

    
    # @dsp.message(Command("start"))
    async def init_user_chat(self, message: types.Message):
        # self.start_stats(self.bot)        
        await message.reply("Добро пожаловать на сервер шизофрения :)))000")


    async def process_message(self, message: types.Message, user: User, msg_text: str):        

        if message.reply_to_message and \
            ('марат передай' in msg_text or 'марат, передай' in msg_text):

            msg_split = msg_text.split()
            cur_alias = msg_split[-1]
            currency = Currency.get_by_alias(cur_alias)
            amount = float(msg_split[-2])
            wallet_amount = user.wallet.amount(currency)
            if amount > wallet_amount:
                res = f"У тебя нет столько {currency.aliases[1]}, кого ты пытаешься наебать? "+\
                    f"У тебя всего лишь {wallet_amount} грамм, иди поработай жопой, нищук."
                await message.reply(res)
                return

            # to_user = User.resource.read(telegram_id = message.reply_to_message.from_user.id)[0]
            to_user = User.user_by_msg(message.reply_to_message)
            transaction = user.send_currency(to_user, currency, amount)

            await message.reply_to_message.reply(f"{to_user}, {user} передал тебе {currency.aliases[1]}, "+ \
                                f"{amount} грамм, запрвляй баян")
        elif message.reply_to_message and \
            ('марат, петух' in msg_text or 'марат петух' in msg_text):
            res = "А твоя мамка дешевая подзаборная шлюха, и что? " +\
                "Ну давай посмотрим сколько этот петушок заработал своим очком: \n"
            
            checked_user = User.user_by_msg(message.reply_to_message)            
            total = 0
            for cr in Currency.currencies():
                amt = checked_user.wallet.amount(cr)
                total += amt
                res += f'{cr.aliases[0]}: {amt} грамм \n'
            if total <= 300:
                res += f'Петушок {checked_user} похож на нищука, скоро пойдёт нахуй отсюда!'
            else:
                res += f'Похоже петушок {checked_user} неплохо работает жопой!'

            await message.reply(res)

        elif msg_text in ('марат, я петух', 'марат я петух'): 
            pass
        elif 'пиво' in message.text.lower():
            await message.reply(f"где сходка?")
        else:
            await message.reply(f"{message.from_user.first_name} - шлюха")


    async def message_handler(self, message: types.Message):
        if message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
            user: User = None
            if not User.tg_user_is_saved(message.from_user):
                user = User.save_user(message.from_user)
            else:
                # user = User.resource.read(telegram_id = message.from_user.id)[0]
                user = User.user_by_msg(message)
            migration()

            bot_id = self.bot.id
            msg_text = message.text.lower()
            if message.text and 'марат' in msg_text:
                try:
                    await self.process_message(message, user, msg_text)
                except Exception as ex:                    
                    await message.reply(f'покукарекай петушок: {ex}\
                         \n {traceback.format_tb(ex.__traceback__)}')                    
                    raise ex
            elif message.reply_to_message.from_user.id == bot_id:
                await message.reply(f"мамку ебал")               
        else:
            await message.answer("пососи потом проси")
            # await message.answer(f'На колени, животное, <b>ты</b>!\n'+
            #                'Прочитай наши правила, и потом не говори, что ты не знал, петух:\n'+
            #                '<a href="https://t.me/polysap_rules/2">Правила полисап</a>', parse_mode="HTML")
        # await dp.bot.send_message(dp.chat.id, 'собачка')

    async def new_member(self, event: ChatMemberUpdated):
        await event.answer(f'На колени, животное, <b>{event.new_chat_member.user.first_name}</b>!\n'+
                           'Прочитай наши правила, и потом не говори, что ты не знал, петух:\n'+
                           '<a href="https://t.me/polysap_rules/2">Правила полисап</a>', parse_mode="HTML")
        # await event.answer(f"<b>Hi, {event.new_chat_member.user.first_name}!</b>",
        #             parse_mode="HTML")
    # async def handle_group_message(self, message: types.Message):
    #     if "бот" in message.text.lower():
    #         await message.reply("я здесь, не ори :)")


        
    async def start(self):
        await self.dsp.start_polling(self.bot, skip_updates=True)

    # async def init_user_chat(self, message):
    #     await message.reply("Добро пожаловать на сервер шизофрения :)))000")

    # async def trade(self, message):
    #     # answer = await dp.bot.send_message(dp.chat.id, 'введите логины и пароли:')
    #     bot = TradingBot(self.config)
    #     bot.start()

    # def start_stats(self, bot):
    #     if not (hasattr(self,'statistic_bot') and self.statistic_bot):
    #         self.statistic_bot = StatisticBot(self.config, bot)
    #     self.statistic_bot.start()

    # async def stats(self, message):
    #     await message.reply("статистика запускается...")
    #     self.start_stats(message.bot)
    #     await message.reply("статистика запущена")

    async def stop(self, message):
        if hasattr(self, "statistic_bot") and not self.statistic_bot == None:
            self.statistic_bot.stop()
            await message.reply("статистика остановлена")
        else:
            await message.reply("ты пес обоссаный")




    def create_parser() -> ArgumentParser:
        parser = ArgumentParser()
        parser.add_argument("--token", help="Telegram Bot API Token")
        parser.add_argument("--chat-id", type=int, help="Target chat id")
        parser.add_argument("--message", "-m", help="Message text to sent", default="Hello, World!")

        return parser