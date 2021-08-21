#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

#TODO list
"""
Autoremoving files
"""

from datetime import datetime
import subprocess
import logging

import emailconfirmation
import config

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

max_file_size = 64 * 1024 * 1024

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO,
    filename='bot.log'
)

logger = logging.getLogger(__name__)

def send_to_printer(file_path):
    #subprocess.run(['lp', file_path])
    print('tipo pechataet')
    logger.info(f'Document {file_path} had sent to printer')


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_text(fr'Hi! This is @innoprintbot you can print some document with my help. We recommend to use PDF format. Send "/auth <your_email>" to confirm that you are student or stuff')
    logger.info(f'User {user.name} started bot')

def auth(update: Update, context: CallbackContext) -> None:
    if emailconfirmation.is_authorized(update.effective_user.id):
        update.message.reply_text('You are already authorized')
        return
    if len(context.args) != 1:
        update.message.reply_text('You need to write only your innopolis email')
        return
    logger.info(f'User {update.effective_user.id} attempts to sign up with email {context.args[0]}')
    if not(emailconfirmation.send_email(update.effective_user.id, context.args[0])):
        update.message.reply_text('Wrong email')    
        return
    update.message.reply_text('Send "/code <code_from_your_email>" to confirm your email')

def code(update: Update, context: CallbackContext) -> None:
    logger.info(f'User {update.effective_user.id} attempts to input a code')
    if len(context.args) != 1:
        update.message.reply_text('You need to write only your code from email')
        return
    user_code = context.args[0]
    if not(emailconfirmation.sign_up(update.effective_user.id, user_code)):
        update.message.reply_text('Wrong code')
        return
    update.message.reply_text('Great! Now you can just send the PDF file and print it')
    
def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('To print your documents just send your PDF file to me')
    logger.info(f'User {update.effective_user.name} request help')

def print_file(update: Update, context: CallbackContext) -> None:
    if not(emailconfirmation.is_authorized(update.effective_user.id)):
        update.message.reply_text('You are not authorized')
        return

    bot = context.bot
    file_id = update.message.document.file_id
    old_file_extension = update.message.document.file_name.split('.')
    if(len(old_file_extension) <= 1):
        update.message.reply_text('Your file is not supported, sorry')
        logger.info(f'User {update.effective_user.name} sent file without extention {update.message.document.file_name}, we dont save it')
        return
    file_name = datetime.utcnow().strftime('%Y%m%d-%H%M%S%f' + old_file_extension[len(old_file_extension)-1])
    file_size = update.message.document.file_size
    
    if file_size > max_file_size:
        update.message.reply_text('Your file is too big')
        logger.info(f'User {update.effective_user.name} sent too big the document {update.message.document.file_name}, we dont save it')
        return

    file_path = "printed_files/" + file_name

    update.message.reply_text('We are downloading your file...')
    new_file = bot.get_file(file_id)
    new_file.download(file_path)

    send_to_printer(file_path=file_path)
    update.message.reply_text('Done! Go to the printer and take your documents :)')
    logger.info(f'User {update.effective_user.name} sent the document {update.message.document.file_name}, we saved it as {file_name} and sent to printer')


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(config.token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("auth", auth))
    dispatcher.add_handler(CommandHandler("code", code))
    dispatcher.add_handler(MessageHandler(Filters.document, print_file))

    # Start the Bot
    updater.start_polling()
    logger.info('Bot started')

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
