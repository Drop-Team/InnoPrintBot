from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types.input_file import InputFile
from aiogram.utils import exceptions
from aiogram.types.message import ParseMode

from datetime import datetime, timedelta, timezone
import os

from bot.command_tools.message_handlers import add_message_handler
from bot.command_tools.callback_query import add_callback_query
from bot.users import UserStates
from bot.printing import tools
from bot.metrics import Metrics
from bot.logger import logger
from bot.consts import FILE_LIFETIME_MINUTES, FILE_LIFETIME_FOR_USER_MINUTES, FILES_PATH
from bot.utils import send_ads

printing_files = []
active_callbacks = dict()


async def check_printing_files(dp):
    tzinfo = timezone(timedelta(hours=3))

    for printing_file in printing_files:
        difference = (datetime.now(tzinfo) - printing_file.created).seconds
        if difference > FILE_LIFETIME_FOR_USER_MINUTES * 60 and not printing_file.expired:
            await dp.bot.edit_message_caption(chat_id=printing_file.msg.chat.id,
                                              message_id=printing_file.msg.message_id,
                                              caption="File has expired")
            printing_file.expired = True

    now = datetime.now()
    for fn in os.listdir(FILES_PATH):
        if fn == ".keep":
            continue

        mode_time = datetime.fromtimestamp(os.path.getmtime(FILES_PATH + fn))
        if (now - mode_time).seconds > FILE_LIFETIME_MINUTES * 60:
            tools.delete_file(FILES_PATH + fn)


class PrintKeyboard:
    edit_pages = InlineKeyboardButton("Edit pages range", callback_data="printing_edit_pages")
    change_copies = InlineKeyboardButton("Change copies count", callback_data="printing_change_copies")
    change_double_sided = InlineKeyboardButton("...", callback_data="printing_change_double_sided")
    confirm = InlineKeyboardButton("Confirm", callback_data="printing_confirm")
    cancel = InlineKeyboardButton("Cancel", callback_data="printing_cancel")

    @classmethod
    def get_markup(cls, printing_file):
        res = InlineKeyboardMarkup()
        res.row(cls.edit_pages)
        res.row(cls.change_copies)
        cls.change_double_sided.text = f"{'Disable' if printing_file.double_sided else 'Enable'} both sides printing"
        res.row(cls.change_double_sided)
        res.row(cls.confirm, cls.cancel)
        return res


class CallbackQueryAnswerKeyboard:
    cancel = KeyboardButton("Cancel")

    @classmethod
    def get_markup(cls):
        res = ReplyKeyboardMarkup(resize_keyboard=True)
        res.row(cls.cancel)
        return res


class ActiveCallback:
    def __init__(self, callback_data, printing_file):
        self.callback_data = callback_data
        self.printing_file = printing_file


def get_printing_file_by_msg(msg):
    for printing_file in printing_files:
        if msg.from_user.id == printing_file.msg.from_user.id and msg.message_id == printing_file.msg.message_id:
            return printing_file
    return None


async def update_printing_file_msg(printing_file):
    markup = PrintKeyboard.get_markup(printing_file) if not printing_file.printed else None
    try:
        return await printing_file.msg.edit_caption(printing_file.generate_caption_text(),
                                                    reply_markup=markup, parse_mode=ParseMode.HTML)
    except exceptions.MessageNotModified:
        return True


@add_message_handler(lambda msg: msg.from_user.id not in active_callbacks,
                     user_state=UserStates.confirmed, not_command=True)
async def print_file(msg):
    user = msg.from_user

    doc = msg.document
    if doc is None:
        return await msg.answer("Please send the document you want to print.")

    await msg.answer("Preparing your document...")

    logger.info(f"{user.mention} ({user.id}) sent document")
    Metrics.print_file_formats.labels(doc.mime_type).inc()

    try:
        temp_path = await tools.download_file(msg.bot, doc)
    except exceptions.FileIsTooBig:
        return await msg.answer("File is too big")

    file_path, is_converted = tools.convert_file(temp_path)
    if not file_path:
        return await msg.answer("File is not supported")

    printing_file = tools.PrintingFile(file_path)

    doc = InputFile(file_path, "preview.pdf")
    target_msg = await msg.answer_document(document=doc, caption=printing_file.generate_caption_text(),
                                           reply_markup=PrintKeyboard.get_markup(printing_file),
                                           parse_mode=ParseMode.HTML)
    printing_file.msg = target_msg
    printing_file.converted = is_converted
    printing_files.append(printing_file)


@add_callback_query(callback_data=PrintKeyboard.change_double_sided.callback_data)
async def change_double_sided_callback(callback_query):
    bot = callback_query.bot
    msg = callback_query.message

    printing_file = get_printing_file_by_msg(msg)

    if printing_file:
        printing_file.double_sided = not printing_file.double_sided
        await update_printing_file_msg(printing_file)

    await bot.answer_callback_query(callback_query.id)


@add_callback_query(lambda cb: cb.data in [PrintKeyboard.change_copies.callback_data,
                                           PrintKeyboard.edit_pages.callback_data])
async def process_input_callbacks(callback_query):
    bot = callback_query.bot
    user = callback_query.from_user
    msg = callback_query.message
    cb_data = callback_query.data

    printing_file = get_printing_file_by_msg(msg)
    if printing_file:
        if cb_data == PrintKeyboard.change_copies.callback_data:
            message = "Send number of copies you need"
        elif cb_data == PrintKeyboard.edit_pages.callback_data:
            message = "Send range of pages you need (For example: 2-6,8,10-11)"
        active_callbacks[user.id] = ActiveCallback(cb_data, printing_file)
        await msg.answer(message, reply_markup=CallbackQueryAnswerKeyboard.get_markup())

    await bot.answer_callback_query(callback_query.id)


@add_callback_query(callback_data=PrintKeyboard.cancel.callback_data)
async def printing_cancel_callback(callback_query):
    bot = callback_query.bot
    user = callback_query.from_user
    msg = callback_query.message

    printing_file = get_printing_file_by_msg(msg)

    if printing_file:
        logger.info(f"{user.mention} ({user.id}) cancelled printing")

        await msg.edit_caption("Printing has been cancelled")
        printing_files.remove(printing_file)

    await bot.answer_callback_query(callback_query.id)


@add_callback_query(callback_data=PrintKeyboard.confirm.callback_data)
async def printing_confirm_callback(callback_query):
    bot = callback_query.bot
    user = callback_query.from_user
    msg = callback_query.message

    printing_file = get_printing_file_by_msg(msg)
    if printing_file:
        printing_file.print()

        if printing_file.printed:
            logger.info(f"{user.mention} ({user.id}) confirmed printing")
            Metrics.printing.labels("requests").inc()
            Metrics.printing.labels("pages").inc(printing_file.get_pages_count())
            Metrics.printing.labels("copies").inc(int(printing_file.copies))
            Metrics.printing.labels("total").inc(int(printing_file.copies) * printing_file.get_pages_count())

            await update_printing_file_msg(printing_file)
            printing_files.remove(printing_file)

            await send_ads(bot, user.id)

        else:
            logger.info(f"Error while printing")
            await msg.answer("An unknown error occurred while printing")

    await bot.answer_callback_query(callback_query.id)


@add_message_handler(lambda msg: msg.from_user.id in active_callbacks)
async def receive_callback_query_answer(msg):
    user = msg.from_user
    text = msg.text.replace(" ", "")

    remove_active_callback = False

    active_callback = active_callbacks[user.id]
    printing_file = active_callback.printing_file

    if text != CallbackQueryAnswerKeyboard.cancel.text and printing_file in printing_files:
        callback_data = active_callback.callback_data

        if callback_data == PrintKeyboard.change_copies.callback_data:
            if tools.validate_copies_count(text):
                printing_file.copies = text
                await update_printing_file_msg(printing_file)
                await msg.answer("Copies count changed", reply_markup=ReplyKeyboardRemove())
                remove_active_callback = True
            else:
                await msg.answer("You should send number of copies. For example: 3")

        elif callback_data == PrintKeyboard.edit_pages.callback_data:
            if tools.validate_pages_range(text):
                printing_file.pages = text
                await update_printing_file_msg(printing_file)
                await msg.answer("Pages range changed", reply_markup=ReplyKeyboardRemove())
                remove_active_callback = True
            else:
                await msg.answer("You should send range of pages. For example: 2-6,8,10-11")

    else:
        await msg.answer("Input cancelled", reply_markup=ReplyKeyboardRemove())
        remove_active_callback = True

    if remove_active_callback:
        active_callbacks.pop(user.id)
