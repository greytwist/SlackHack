from slackbot.bot import respond_to
import re

@respond_to('hello', re.IGNORECASE)
def hello(message):
    message.reply('hello!')

@respond_to('hey bro', re.IGNORECASE)
def hey_bro(message):
    message.reply('getting ready to watch some bball!')
