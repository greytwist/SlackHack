# -*- coding: utf8 -*-

from __future__ import print_function
import os
import json
import logging
import time
import slacker

from websocket import (
    create_connection, WebSocketException, WebSocketConnectionClosedException
)

from slackbot.utils import to_utf8

logger = logging.getLogger(__name__)

class SlackClient(object):
    def __init__(self, token, connect=True):
        self.token = token
        self.username = None
        self.domain = None
        self.login_data = None
        self.websocket = None
        self.users = {}
        self.name_chan_dict = {}
        self.channels = {}
        self.connected = False
        self.webapi = slacker.Slacker(self.token)

        if connect:
            self.rtm_connect()

    def rtm_connect(self):
        reply = self.webapi.rtm.start().body
        self.parse_slack_login_data(reply)

    def reconnect(self):
        while True:
            try:
                self.rtm_connect()
                logger.warning('reconnected to slack rtm websocket')
                return
            except:
                logger.exception('failed to reconnect')
                time.sleep(1)

    def parse_slack_login_data(self, login_data):
        self.login_data = login_data
        self.domain = self.login_data['team']['domain']
        self.username = self.login_data['self']['name']
        self.users = dict((u['id'], u) for u in login_data['users'])
        self.parse_channel_data_for_login(login_data['channels'])
        self.parse_channel_data(login_data['groups'])
        self.parse_channel_data(login_data['ims'])
        
        #for key in self.channels:
        #    logger.info( self.channels.get( key ) )

        try:
            self.websocket = create_connection(self.login_data['url'])
            self.websocket.sock.setblocking(0)
        except:
            raise SlackConnectionError

    def parse_channel_data(self, channel_data):              
        self.channels.update({c['id']: c for c in channel_data})
      
    def parse_channel_data_for_login(self, channel_data):              
        for c in channel_data:
            if 'name' in c:
                self.name_chan_dict =  {c['name']:c['id'] }
                
        self.channels.update({c['id']: c for c in channel_data})
       
    

    def send_to_websocket(self, data):
        """Send (data) directly to the websocket."""
        data = json.dumps(data)
        self.websocket.send(data)

    def ping(self):
        return self.send_to_websocket({'type': 'ping'})

    def websocket_safe_read(self):
        """Returns data if available, otherwise ''. Newlines indicate multiple messages """
        data = ''
        while True:
            try:
                data += '{0}\n'.format(self.websocket.recv())
            except WebSocketException, e:
                if isinstance(e, WebSocketConnectionClosedException):
                    logger.warning('lost websocket connection, try to reconnect now')
                else:
                    logger.warning('websocket exception: %s', e)
                self.reconnect()
            except:
                return data.rstrip()

    def rtm_read(self):
        json_data = self.websocket_safe_read()
        data = []
        if json_data != '':
            for d in json_data.split('\n'):
                data.append(json.loads(d))
        return data

    def rtm_send_message(self, channel, message):
        message_json = {'type': 'message', 'channel': channel, 'text': message}
        self.send_to_websocket(message_json)

    def upload_file(self, channel, fname, fpath, comment):
        fname = fname or to_utf8(os.path.basename(fpath))
        self.webapi.files.upload(fpath,
                                 channels=channel,
                                 filename=fname,
                                 initial_comment=comment)

    def send_channel_message(self, channel, message):
        message_json = {'type': 'message', 'channel': channel, 'text': message}
        self.send_to_websocket(message_json)

    def get_channel(self, channel_id):
        return Channel(self, self.channels[channel_id])

    def find_user_by_name(self, username):
        for userid, user in self.users.iteritems():
            if user['name'] == username:
                return userid
                
class SlackConnectionError(Exception):
    pass

class Channel(object):
    def __init__(self, slackclient, body):
        self._body = body
        self._client = slackclient

    def upload_file(self, fname, fpath, initial_comment=''):
        self._client.upload_file(
            self._body['id'],
            to_utf8(fname),
            to_utf8(fpath),
            to_utf8(initial_comment)
        )
