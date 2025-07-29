#!/usr/bin/env python3

import argparse
import requests
import urllib.parse

# Howto: https://hackernoon.com/how-to-create-a-simple-bash-shell-script-to-send-messages-on-telegram-lcz31bx
# Note: Need to make the bot an admin of the channel for it to see updates

ENDPOINT_URL = f'https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s'

class TelegramDestination:
    def __init__(self, api_token: str, chat_id: str):
        self.api_token = api_token
        self.chat_id = chat_id

    def send(self, message: str):
        print(" - Sending message: %s" % message)
        message_text_encoded = urllib.parse.quote(message)
        url = ENDPOINT_URL % (self.api_token, self.chat_id, message_text_encoded)

        rv = requests.get(url)
        if rv.status_code != 200:
            raise Exception("Invalid return code: %d" % rv.status_code)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("message")
    args = parser.parse_args()
    sender = TelegramDestination()
    sender.send_message(args.message)
