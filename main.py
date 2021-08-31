#!/usr/bin/env python

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ContentTypes
from prometheus_client import start_http_server

from datetime import datetime
import asyncio
import logging
import socket

import config
from config import TOKEN
import auth
import files
from metrics import Metrics

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

change_email_kb = InlineKeyboardMarkup().add(InlineKeyboardButton("Change email", callback_data="change_email"))
resend_code_kb = InlineKeyboardMarkup().add(InlineKeyboardButton("Resend code", callback_data="resend_code"))

LETTER_SENDING_COOLDOWN = 60
CODE_ATTEMPT_COOLDOWN = 5
CODE_ACTIVE_MINUTES = 10
PRINTING_COOLDOWN = 30
CHECK_FILES_COOLDOWN = 60

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO,
    filename='bot.log'
)

logger = logging.getLogger(__name__)


def state_filter(message, state):
    user_id = message.from_user.id
    if user_id not in auth.users_data:
        auth.users_data[user_id] = {"state": auth.UserStates.init}
    return auth.users_data[user_id]["state"] == state


@dp.errors_handler()
async def exception(update, error):
    Metrics.errors.inc()


@dp.message_handler(commands=["start"])
async def process_start_command(message: types.Message):
    Metrics.start_command.labels("success").inc()
    logger.info(f"User {message.from_user.username} ({message.from_user.id}) started bot")
    await message.answer("Hi! This is @innoprintbot you can print some document with my help.\n"
                         "First send your innopolis email to verify you are a student or staff.")


@dp.message_handler(commands=["help"])
async def process_help_command(message: types.Message):
    Metrics.help_command.labels("success").inc()
    logger.info(f"User {message.from_user.username} ({message.from_user.id}) used help command")
    await message.answer("To print just send your file to me\n"
                         "Please *don't shut down* the printer. It causes connection problems. "
                         "Printer will suspend automatically!\n\n"
                         "Support: @blinikar and @KeepError\n"
                         "GitHub: https://github.com/blinikar/innoprintbot",
                         parse_mode="Markdown")


@dp.message_handler(lambda message: message.from_user.id in config.ADMINS, commands=["ip"])
async def process_ip_command(message: types.Message):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    await message.answer(ip)


async def send_code(user_id):
    if "letter_sent" in auth.users_data[user_id]:
        sec = (datetime.now() - auth.users_data[user_id]["letter_sent"]).total_seconds()
        difference = int(LETTER_SENDING_COOLDOWN - sec)
        if difference > 0:
            Metrics.code_sending.labels("cooldown").inc()
            return await bot.send_message(user_id, f"You can request new code only in {difference} sec.")

    if not auth.send_mail(user_id):
        Metrics.code_sending.labels("error_sending_letter").inc()
        return await bot.send_message(user_id, "There was something error sending letter. "
                                               "Please send your innopolis email.")

    auth.users_data[user_id]["letter_sent"] = datetime.now()
    auth.users_data[user_id]["code_sent_to_email"] = datetime.now()
    auth.users_data[user_id]["state"] = auth.UserStates.requested_code
    Metrics.code_sending.labels("success").inc()
    await bot.send_message(user_id, "Check your email and send confirmation code within 10 minutes.",
                           reply_markup=resend_code_kb)


@dp.message_handler(lambda message: state_filter(message, auth.UserStates.init), content_types=ContentTypes.ANY)
async def process_email_message(message: types.Message):
    logger.info(f"User {message.from_user.username} ({message.from_user.id}) tried to send email")
    user_id = message.from_user.id
    if not message.text or not auth.validate_email(message.text):
        Metrics.email_setting.labels("validation_failed").inc()
        return await message.answer("You need to send your innopolis email.")

    auth.users_data[user_id]["email"] = message.text
    Metrics.email_setting.labels("success").inc()
    await message.answer(f"Email {message.text} has been set. Now you need to confirm it.",
                         reply_markup=change_email_kb)

    await send_code(user_id)


@dp.callback_query_handler(lambda cb: cb.data == "change_email")
async def process_change_email_callback(callback_query: types.CallbackQuery):
    logger.info(f"User {callback_query.from_user.username} ({callback_query.from_user.id}) tried to change email")
    user_id = callback_query.from_user.id
    if auth.users_data[user_id]["state"] == auth.UserStates.confirmed:
        Metrics.email_changing.labels("already_authorized").inc()
        await callback_query.answer("You are already authorized.")
    else:
        auth.users_data[user_id]["state"] = auth.UserStates.init
        Metrics.email_changing.labels("success").inc()
        await bot.send_message(user_id, "Send new innopolis email.")
    await bot.answer_callback_query(callback_query.id)


@dp.message_handler(lambda message: state_filter(message, auth.UserStates.requested_code),
                    content_types=ContentTypes.ANY)
async def process_code_message(message: types.Message):
    logger.info(f"User {message.from_user.username} ({message.from_user.id}) tried to enter a code")
    user_id = message.from_user.id

    if not message.text:
        Metrics.code_attempt.labels("validation_failed").inc()
        return await message.answer(f"You need to send confirmation code.")

    if "code_attempt" in auth.users_data[user_id]:
        Metrics.code_attempt.labels("cooldown").inc()
        sec = (datetime.now() - auth.users_data[user_id]["code_attempt"]).total_seconds()
        difference = int(CODE_ATTEMPT_COOLDOWN - sec)
        if difference > 0:
            return await message.answer(f"You can attempt a code in {difference} sec.")

    if "code_sent_to_email" in auth.users_data[user_id]:
        minutes_past = int((datetime.now() - auth.users_data[user_id]["code_sent_to_email"]).total_seconds()) // 60
        if minutes_past >= CODE_ACTIVE_MINUTES:
            Metrics.code_attempt.labels("inactive").inc()
            return await message.answer(f"Code is already inactive. You need to request it again.")

    auth.users_data[user_id]["code_attempt"] = datetime.now()

    if not auth.validate_code(message.from_user.id, message.text):
        Metrics.code_attempt.labels("incorrect").inc()
        return await message.answer("Code is incorrect")
    auth.users_data[message.from_user.id]["state"] = auth.UserStates.confirmed
    auth.save_file()
    Metrics.code_attempt.labels("success").inc()
    await message.answer("Great! Now just send me file and I will print it.")


@dp.callback_query_handler(lambda cb: cb.data == "resend_code")
async def process_resend_code_callback(callback_query: types.CallbackQuery):
    logger.info(f"User {callback_query.from_user.username} ({callback_query.from_user.id}) requested code resending")
    user_id = callback_query.from_user.id
    if auth.users_data[user_id]["state"] == auth.UserStates.init:
        Metrics.code_resending.labels("email_not_set").inc()
        await callback_query.answer("First you need to set up your email.")
    elif auth.users_data[user_id]["state"] == auth.UserStates.confirmed:
        Metrics.code_resending.labels("already_authorized").inc()
        await callback_query.answer("You are already authorized.")
    else:
        Metrics.code_resending.labels("success").inc()
        await send_code(user_id)
    await bot.answer_callback_query(callback_query.id)


@dp.message_handler(lambda message: state_filter(message, auth.UserStates.confirmed), content_types=ContentTypes.ANY)
async def process_print_message(message: types.Message):
    doc = message.document
    if doc is None:
        Metrics.printing.labels("not_doc").inc()
        return await message.answer("Please send the document you want to print.")

    user_id = message.from_user.id
    if "last_print" in auth.users_data[user_id]:
        sec = (datetime.now() - auth.users_data[user_id]["last_print"]).total_seconds()
        difference = int(PRINTING_COOLDOWN - sec)
        if difference > 0:
            Metrics.printing.labels("cooldown").inc()
            return await message.answer(f"You can print again in {difference} sec.")

    msg = await message.answer("Getting your file ready...")
    file_path = await files.download_file(bot, doc)
    if file_path is None:
        Metrics.printing.labels("big_file").inc()
        return await msg.edit_text("Your file is too big.")

    logger.info(f"User {message.from_user.username} ({message.from_user.id}) prints document")

    auth.users_data[user_id]["last_print"] = datetime.now()
    files.print_file(file_path)
    Metrics.printing.labels("success").inc()
    await msg.edit_text("Done! Go to the printer on 5th floor and take your documents.")


def repeat(coro, loop):
    asyncio.ensure_future(coro(), loop=loop)
    loop.call_later(CHECK_FILES_COOLDOWN, repeat, coro, loop)


if __name__ == "__main__":
    start_http_server(8000)
    Metrics.printing_enabled.set(int(config.PRINTING_ENABLED))

    loop = asyncio.get_event_loop()
    loop.call_later(CHECK_FILES_COOLDOWN, repeat, files.check_files, loop)

    executor.start_polling(dp)
