import os

DEBUG = False

PLUGINS = [
    'slackbot.plugins',
    'mybot.plugins',
]

#for key in os.environ:
#    print key
#    if key[:9] == 'SLACKBOT_':
#        name = key[9:]
#        globals()[name] = os.environ[key]

try:
    from local_settings import *
except ImportError:
    pass
