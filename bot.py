#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
The Imitation Bot. Parse the token into the start_bot function or with -q if launching as script.
'''
import os
import re
import string
import argparse
import logging
import markovify

import telegram
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                            MessageHandler, Updater)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

### BOT COMMANDS ###

table = str.maketrans('', '', string.punctuation)

def clean_text(text):
    text = re.sub(r'^https?:\/\/.*[\r\n]*', '', text, flags=re.MULTILINE)
    text = re.split(r'\n|\.',text)
    text = [x.translate(table).lower().strip(' ') for x in text]
    text = list(filter(bool, text))
    return text

def start(update, context):
    '''
    Define the /start command
    '''
    update.message.reply_text(text="""This bot imitates the chat. Use with /imitate.""")

def add_message(update, context):
    '''
    Add a new item to the list, try to assign it to a group
    '''
    chat_id = str(update.message.chat_id)
    text = update.message.text
    text = clean_text(text)
    with open(os.path.join('data', chat_id), 'a') as file:
        for i in text:
            file.write(i +  '\n')

def imitate(update, context):
    chat_id = str(update.message.chat_id)
    with open(os.path.join('data', chat_id)) as f:
        text = f.read()
        text_model = markovify.NewlineText(text)
        imit = text_model.make_short_sentence(140)
        if imit:
            update.message.reply_text(imit)
        else:
            update.message.reply_text('Not enough data yet, please keep chatting')

def error(update, context):
    '''
    Print warnings in case of errors
    '''
    logger.warning('Update "%s" caused error "%s"',
                    update,
                    context.error)

def start_bot(token):
    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('imitate', imitate))
    dispatcher.add_handler(MessageHandler(Filters.text, add_message))
    dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-t", help="your bot API token", type=str)
    args = parser.parse_args()
    start_bot(token=args.t)
