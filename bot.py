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
import nltk

import telegram
from telegram.ext import (CommandHandler, Filters,
                            MessageHandler, Updater)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

### BOT COMMANDS ###

table = str.maketrans('', '', string.punctuation)

class POSifiedText(markovify.NewlineText):
    def word_split(self, sentence):
        words = re.split(self.word_split_pattern, sentence)
        words = [ "::".join(tag) for tag in nltk.pos_tag(words) ]
        return words

    def word_join(self, words):
        sentence = " ".join(word.split("::")[0] for word in words)
        return sentence


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
    update.message.reply_text(text="""This bot imitates the chat.
    /imitate creates a normal message attempt,
    /with <word> attempts to start a message with <word>
    /long <number> attempts to create a message that is <number> of characters long
    /nltk attempts to create a message with pos tags from nltk (Can take a lot of time!)
    """)

def add_message(update, context):
    '''
    Add a new item to the list, try to assign it to a group
    '''
    chat_id = str(update.message.chat_id)
    text = update.message.text
    if " " in text:
        text = clean_text(text)
        with open(os.path.join('data', chat_id), 'a') as file:
            for i in text:
                file.write(i +  '\n')

def imitate(update, context):
    chat_id = str(update.message.chat_id)
    with open(os.path.join('data', chat_id)) as f:
        text = f.read()
        text_model = markovify.NewlineText(text)
        imit = text_model.make_sentence(tries=100)
        if imit:
            update.message.reply_text(imit)
        else:
            update.message.reply_text('Not enough data yet, please keep chatting')

def imitate_nltk(update, context):
    chat_id = str(update.message.chat_id)
    with open(os.path.join('data', chat_id)) as f:
        text = f.read()
        text_model = POSifiedText(text)
        imit = text_model.make_sentence(tries=100)
        if imit:
            update.message.reply_text(imit)
        else:
            update.message.reply_text('Not enough data yet, please keep chatting')

def imitate_with(update, context):
    chat_id = str(update.message.chat_id)
    with open(os.path.join('data', chat_id)) as f:
        text = f.read()
        text_model = markovify.NewlineText(text)
        try:
            imit = text_model.make_sentence_with_start(context.args[0], tries=100, strict=False)
            if imit:
                update.message.reply_text(imit)
            else:
                update.message.reply_text('Not enough data yet, please keep chatting')
        except:
            update.message.reply_text('Not enough data yet, please keep chatting')

def imitate_long(update, context):
    chat_id = str(update.message.chat_id)
    with open(os.path.join('data', chat_id)) as f:
        text = f.read()
        text_model = markovify.NewlineText(text)
        count = int(context.args[0])
        min_chars = count - (count//4)
        max_chars = count + (count//4)
        imit = text_model.make_short_sentence(max_chars=max_chars, min_chars=min_chars, tries=100)
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
    dispatcher.add_handler(CommandHandler('with', imitate_with))
    dispatcher.add_handler(CommandHandler('long', imitate_long))
    dispatcher.add_handler(CommandHandler('nltk', imitate_nltk))
    dispatcher.add_handler(MessageHandler(Filters.text, add_message))
    dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-t", help="your bot API token", type=str)
    args = parser.parse_args()
    start_bot(token=args.t)
