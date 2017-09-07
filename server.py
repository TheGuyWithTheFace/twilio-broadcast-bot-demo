#!/usr/bin/env python3

from twilio.rest import Client

from http.server import BaseHTTPRequestHandler, HTTPServer

import json

INFO_FILE = 'server.txt'
TWILIO_FILE = 'twilio.txt'
NUMBERS_FILE = 'numbers.txt' # numbers to text on broadcast
TRIGGER_STR = '!broadcast '

# Load configs. These should really be in a proper config file rather than a
# bunch of unlabled values in miscellaneous files, but oh well.
with open(INFO_FILE) as f:
    SERVER_ADDR = f.readline().rstrip('\n')
    SERVER_PORT = int(f.readline().rstrip('\n'))

with open(TWILIO_FILE) as f:
    TWILIO_SID = f.readline().rstrip('\n')
    TWILIO_AUTH_TOKEN = f.readline().rstrip('\n')
    TWILIO_PHONE_NUMBER = f.readline().rstrip('\n')

PHONE_NUMBERS = []
with open(NUMBERS_FILE) as f:
    for line in f:
        PHONE_NUMBERS.append(line)


class TestRequestHandler(BaseHTTPRequestHandler):

    _client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

    # POST
    def do_POST(self) -> None:
        print('recieved message')

        # data from groupme
        request = str(self._get_body_data(), 'utf-8')
        from_groupme = json.loads(request)

        # semi-relevant info
        name = from_groupme["name"]
        group = from_groupme["group_id"]
        text = from_groupme["text"]
        sender_type = from_groupme["sender_type"]

        # bot should not respond to itself
        if sender_type != "user": 
            return 

        if text.startswith(TRIGGER_STR):
            self._broadcast(text.replace(TRIGGER_STR, '', 1))

    def _broadcast(self, message: str) -> None:
        print('broadcasting \'{}\' to {} numbers...'.format(message,
                                                            len(PHONE_NUMBERS)))
        for number in PHONE_NUMBERS:
            self._client.messages.create(
                    to=number,
                    from_=TWILIO_PHONE_NUMBER,
                    body=message
            )

    def _get_body_data(self) -> str:
        content_length = int(self.headers['Content-Length'])
        return self.rfile.read(content_length)


if __name__ == '__main__':
    print('starting server...')
    server_address = (SERVER_ADDR, SERVER_PORT)
    httpd = HTTPServer(server_address, TestRequestHandler)
    print('running server...')
    httpd.serve_forever() # and ever and ever and ever
