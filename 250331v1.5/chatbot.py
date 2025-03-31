## this file is based on version 13.7 of python telegram chatbot
## and version 1.26.18 of urllib3
## chatbot.py
from telegram import Update
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
CallbackContext)
import configparser
import logging
import os
from Chat_GPT_HKBU import HKBU_ChatGPT
from my_firebase import users

global chatgpt


def main():
    # Load your token and create an Updater for your Bot
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CONFIG_PATH = os.path.join(BASE_DIR, 'config.ini')
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']),use_context=True)
    dispatcher = updater.dispatcher
    

    # You can set this logging module, so you will know when
    # and why things do not work as expected Meanwhile, update your config.ini as:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s \
    - %(message)s', level= logging.INFO)


# dispatcher for chatgpt
    global chatgpt
    chatgpt = HKBU_ChatGPT(config)


    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command),
    equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("add", add_command))
    dispatcher.add_handler(CommandHandler("list", list_command))
    dispatcher.add_handler(CommandHandler("delete", delete_command))
    # To start the bot:
    updater.start_polling()
    updater.idle()

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('You can use command to add,list,delete user info\
                              /add + user_name + Game + Social + VR\
                              /list\
                              /delete + user_name')
    
def add_command(update: Update, context: CallbackContext) -> None:
    try:
        chatgpt.config_user(update.message.text)
        update.message.reply_text('Add successfully ')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add + user_name + Game + Social + VR')

def list_command(update: Update, context: CallbackContext) -> None:
    try:
        all_user_info = users.list_users()
        update.message.reply_text(all_user_info)
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /list')

def delete_command(update: Update, context: CallbackContext) -> None:
    try:
        logging.info(context.args[0])
        name = context.args[0]
        msg = users.delete_user(name)
        update.message.reply_text(msg)
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /delete + user_name')    


def equiped_chatgpt(update, context):
    global chatgpt
    reply_message = chatgpt.submit(update.message.text)
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

if __name__ == '__main__':
    main()   
