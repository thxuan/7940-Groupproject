## this file is based on version 13.7 of python telegram chatbot
## and version 1.26.18 of urllib3
## chatbot.py
from telegram import Update
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
CallbackContext)
import configparser
import logging
import redis
import os
from Chat_GPT_HKBU import HKBU_ChatGPT

global redis1
global chatgpt

def main():
    # Load your token and create an Updater for your Bot
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CONFIG_PATH = os.path.join(BASE_DIR, 'config.ini')
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']),use_context=True)
    dispatcher = updater.dispatcher

    global redis1
    redis1 = redis.Redis(host=(config['REDIS']['HOST']),
                        password=(config['REDIS']['PASSWORD']),
                        port=(config['REDIS']['REDISPORT']),
                        decode_responses=(config['REDIS']['DECODE_RESPONSE']),
                        username=(config['REDIS']['USER_NAME']))
    
    # You can set this logging module, so you will know when
    # and why things do not work as expected Meanwhile, update your config.ini as:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s \
    - %(message)s', level= logging.INFO)

    # register a dispatcher to handle message: here we register an echo dispatcher
    # echo_handler = MessageHandler(Filters.text & (~Filters.command),echo)
    # dispatcher.add_handler(echo_handler)

# dispatcher for chatgpt
    global chatgpt
    chatgpt = HKBU_ChatGPT(config)
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command),
    equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("get", get))
    dispatcher.add_handler(CommandHandler("delete", delete))
    dispatcher.add_handler(CommandHandler("hello", hello))

    # To start the bot:
    updater.start_polling()
    updater.idle()

# def echo(update,context):
#     reply_message = update.message.text.upper()
#     logging.info("Update: " + str(update))
#     logging.info("context: " + str(context))
#     context.bot.send_message(chat_id = update.effective_chat.id, 
#         text = reply_message) 

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')

def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global redis1
        logging.info(context.args[0])
        redis1.incr(context.args[0])
        update.message.reply_text('Add successfully ')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')

def get(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0] # /add keyword <-- this should store the keyword
        if(redis1.get(msg) is None):
            count = 0
        else:
            count = redis1.get(msg)
        update.message.reply_text('You have said ' + msg + ' for ' +  
                                  str(count) + ' times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')

def delete(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global redis1
        logging.info(context.args[0])
        redis1.delete(context.args[0])
        update.message.reply_text('Delete successfully.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /delete <keyword>')


def hello(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0]
        update.message.reply_text('Good day, ' + msg + '! ' )
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /hello <keyword>')

def equiped_chatgpt(update, context):
    global chatgpt
    reply_message = chatgpt.submit(update.message.text)
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

if __name__ == '__main__':
    main()   
