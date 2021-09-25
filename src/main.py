import os

import emoji
import telebot
from loguru import logger

from constants import keyboards, keys, states


class Bot:
    def __init__(self):
        telegram_bot_token = os.environ['TELEGRAMBOT_TOKEN']
        self.bot = telebot.TeleBot(
            telegram_bot_token, parse_mode='HTML'
        ) # You can set parse_mode by default. HTML or MARKDOWN

        self.respond_welcome = self.bot.message_handler(commands=['start', 'help'])(self.respond_welcome)
        self.respond_text = self.bot.message_handler(func=lambda message: True)(self.respond_text)

        # keep users state
        self.users = dict()

    def run(self):
        logger.info('Running Bot...')
        self.bot.polling()

    def respond_welcome(self, message):
        self.set(message)
        self.send_message(f':high_voltage: Hey <b>{self.name}</b>!', reply_markup=keyboards.main)

        self.set_state(states.init)

    def respond_text(self, message):
        self.set(message)

        message.text = emoji.demojize(message.text)

        # talking to stranger
        if self.get_state() == states.talking:
            self.send_message(message.text, self.users[self.chat_id]['random_connection'])

        # start looking for strangers to connect
        elif message.text == keys.random_connect:
            self.send_message(
                ':hourglass_not_done: Waiting for someone to connect...',
                reply_markup=keyboards.back
            )
            self.set_state(states.random_connect)

        # settings
        elif message.text == keys.settings:
            self.send_message(
                keys.settings,
                reply_markup=keyboards.back
            )

            self.set_state(states.settings)

        # back
        elif message.text == keys.back:
            self.send_message(
                keys.back,
                reply_markup=keyboards.main,
            )
            self.set_state(states.init)

        # connect to stranger
        if self.get_state() == states.random_connect:
            self.connect()

    def connect(self):
        # find someone in random connect state
        for chat_id, info in self.users.items():
            if chat_id == self.chat_id:
                continue

            if info['state'] != states.random_connect:
                continue

            self.send_message(
                f':check_mark_button: Connected to {chat_id}. Start talking!',
                chat_id=self.chat_id,
                reply_markup=keyboards.talking,
            )
            self.send_message(
                f':check_mark_button: Connected to {self.chat_id}. Start talking!',
                chat_id=chat_id,
                reply_markup=keyboards.talking,
            )

            self.users[self.chat_id]['random_connection'] = chat_id
            self.users[chat_id]['random_connection'] = self.chat_id

            self.set_state(states.talking, self.chat_id)
            self.set_state(states.talking, chat_id)

    def set(self, message):
        # personal information
        self.message = message
        self.name = message.chat.first_name
        if message.chat.last_name:
            self.name = f'{self.name} {message.chat.last_name}'

        self.chat_id = message.chat.id
        if not self.users.get(self.chat_id):
            self.users[self.chat_id] = dict(
                username = message.chat.username,
            )

    def set_state(self, state, chat_id=None):
        if chat_id is None:
            chat_id = self.chat_id

        self.users[chat_id]['state'] = state
        logger.info(f'Set state to --> "{state}"')

    def get_state(self):
        return self.users[self.chat_id].get('state')

    def send_message(self, bot_response, chat_id=None, reply_markup=None, emojize=True):
        if emojize:
            bot_response = emoji.emojize(bot_response)

        if not chat_id:
            chat_id = self.message.chat.id

        self.bot.send_message(chat_id, bot_response, reply_markup=reply_markup)

if __name__ == '__main__':
    bot = Bot()
    bot.run()
