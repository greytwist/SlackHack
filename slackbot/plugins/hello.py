from slackbot.bot import respond_to
import re

@respond_to('hello', re.IGNORECASE)
def hello(message):
    message.reply('hello!')

@respond_to('sup', re.IGNORECASE)
def sup(message):
    message.reply('nothing, sup which you?')
