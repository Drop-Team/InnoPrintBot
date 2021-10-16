from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.input_file import InputFile
from aiogram.utils import exceptions
from aiogram.types.message import ParseMode

from datetime import datetime, timedelta, timezone
import io

from bot.command_tools.message_handlers import add_message_handler
from bot.command_tools.callback_query import add_callback_query
from bot.users import UserStates, users, save_file
from bot.scanning import tools
from bot.metrics import Metrics
from bot.logger import logger
from bot.consts import SCANNING_JOB_LIFETIME_MINUTES
from bot.utils import send_ads

scanning_jobs = []
active_callbacks = dict()


async def check_scanning_jobs(dp):
    tzinfo = timezone(timedelta(hours=3))
    for scanning_job in scanning_jobs:
        difference = (datetime.now(tzinfo) - scanning_job.created).seconds
        if difference > SCANNING_JOB_LIFETIME_MINUTES * 60:
            await dp.bot.edit_message_text(chat_id=scanning_job.msg.chat.id,
                                           message_id=scanning_job.msg.message_id,
                                           text="Scanning has expired")
            scanning_jobs.remove(scanning_job)


class ActiveCallback:
    def __init__(self, callback_data, scanning_job, msg=None):
        self.callback_data = callback_data
        self.scanning_job = scanning_job
        self.msg = msg


class ScanKeyboard:
    change_input = InlineKeyboardButton("...", callback_data="scanning_change_input")
    change_dpi = InlineKeyboardButton("Change quality (DPI)", callback_data="scanning_change_dpi")
    change_double_sided = InlineKeyboardButton("...", callback_data="scanning_change_double_sided")
    confirm = InlineKeyboardButton("Confirm", callback_data="scanning_confirm")
    cancel = InlineKeyboardButton("Cancel", callback_data="scanning_cancel")

    @classmethod
    def get_markup(cls, scanning_job):
        res = InlineKeyboardMarkup()

        other_scan_input = tools.ScanInputs.ADF if scanning_job.scan_input == tools.ScanInputs.Platen \
            else tools.ScanInputs.Platen
        cls.change_input.text = "Change input to " + other_scan_input.name

        res.row(cls.change_input)
        if scanning_job.scan_input.available_double_side:
            cls.change_double_sided.text = ("Disable" if scanning_job.double_sided else "Enable") + " double sided " \
                                                                                                    "scanning"
            res.row(cls.change_double_sided)
        res.row(cls.change_dpi)
        res.row(cls.confirm, cls.cancel)
        return res


class ChangeDPIKeyboard:
    available_values = [200, 300, 400, 600]

    @classmethod
    def get_markup(cls):
        res = InlineKeyboardMarkup()
        res.row(*[InlineKeyboardButton(str(value), callback_data=f"scanning_dpi_{value}")
                  for value in cls.available_values])
        return res


def get_scanning_job_by_msg(msg):
    for scanning_job in scanning_jobs:
        if msg.from_user.id == scanning_job.msg.from_user.id and msg.message_id == scanning_job.msg.message_id:
            return scanning_job
    return None


async def update_scanning_job_msg(scanning_job):
    markup = ScanKeyboard.get_markup(scanning_job) if not scanning_job.scanned else None
    try:
        return await scanning_job.msg.edit_text(scanning_job.generate_message_text(), reply_markup=markup,
                                                parse_mode=ParseMode.HTML)
    except exceptions.MessageNotModified:
        return True


async def send_help_message(bot, user_id):
    help_text = "<b>Scanning tutorial</b>\n\n" \
                "<i>You can choose two scanner types (see image):</i>\n" \
                "<b>Platen</b> - Classical scanner, supports only one page\n" \
                "<b>ADF</b> - Automatic feeder, you can put up to 50 pages, supports double-sided scanning\n\n" \
                "Quality of result depends on DPI, but remember that higher resolution causes " \
                "higher file sizes and increases scanning duration\n\n" \
                "You will receive a PDF document"
    await bot.send_photo(user_id, photo=open("bot/src/scanning_tutorial.png", "rb"), caption=help_text,
                         parse_mode=ParseMode.HTML)
    users[user_id].used_scan = True
    save_file()


@add_message_handler(commands=["scan"], user_state=UserStates.confirmed)
async def scan_command(msg):
    user = msg.from_user

    if not users[user.id].used_scan:
        await send_help_message(msg.bot, user.id)

    new_job = tools.ScanningJob()

    new_msg = await msg.answer(new_job.generate_message_text(), reply_markup=ScanKeyboard.get_markup(new_job),
                               parse_mode=ParseMode.HTML)
    new_job.msg = new_msg

    scanning_jobs.append(new_job)


@add_message_handler(commands=["help_scan"], user_state=UserStates.confirmed)
async def help_scan_command(msg):
    await send_help_message(msg.bot, msg.from_user.id)


@add_callback_query(callback_data=ScanKeyboard.change_input.callback_data)
async def scanning_change_input_callback(callback_query):
    bot = callback_query.bot
    msg = callback_query.message

    scanning_job = get_scanning_job_by_msg(msg)
    if scanning_job:
        if scanning_job.scan_input == tools.ScanInputs.ADF:
            scanning_job.scan_input = tools.ScanInputs.Platen
        else:
            scanning_job.scan_input = tools.ScanInputs.ADF

        await update_scanning_job_msg(scanning_job)

    await bot.answer_callback_query(callback_query.id)


@add_callback_query(callback_data=ScanKeyboard.change_dpi.callback_data)
async def scanning_change_dpi_callback(callback_query):
    bot = callback_query.bot
    user = callback_query.from_user
    msg = callback_query.message
    cb_data = callback_query.data

    scanning_job = get_scanning_job_by_msg(msg)
    if scanning_job:
        wait_msg = await msg.answer("Select DPI", reply_markup=ChangeDPIKeyboard.get_markup())
        active_callbacks[user.id] = ActiveCallback(cb_data, scanning_job, wait_msg)

    await bot.answer_callback_query(callback_query.id)


@add_callback_query(lambda cb: cb.data.startswith("scanning_dpi_"))
async def process_answer_change_dpi(callback_query):
    bot = callback_query.bot
    user = callback_query.from_user
    msg = callback_query.message
    cb_data = callback_query.data

    active_callback = active_callbacks.get(user.id, None)
    if active_callback:
        value = int(cb_data.split("_")[-1])
        active_callback.scanning_job.dpi = value
        await update_scanning_job_msg(active_callback.scanning_job)
        await msg.delete()

    await bot.answer_callback_query(callback_query.id)


@add_callback_query(callback_data=ScanKeyboard.change_double_sided.callback_data)
async def scanning_change_double_sided_callback(callback_query):
    bot = callback_query.bot
    msg = callback_query.message

    scanning_job = get_scanning_job_by_msg(msg)
    if scanning_job:
        scanning_job.double_sided = not scanning_job.double_sided

        await update_scanning_job_msg(scanning_job)

    await bot.answer_callback_query(callback_query.id)


@add_callback_query(callback_data=ScanKeyboard.cancel.callback_data)
async def scanning_cancel_callback(callback_query):
    bot = callback_query.bot
    user = callback_query.from_user
    msg = callback_query.message

    scanning_job = get_scanning_job_by_msg(msg)
    if scanning_job:
        logger.info(f"{user.mention} ({user.id}) confirmed scanning")

        await msg.edit_text("Scanning has been cancelled")
        scanning_jobs.remove(scanning_job)

    await bot.answer_callback_query(callback_query.id)


@add_callback_query(callback_data=ScanKeyboard.confirm.callback_data)
async def scanning_confirm_callback(callback_query):
    bot = callback_query.bot
    user = callback_query.from_user
    msg = callback_query.message

    scanning_job = get_scanning_job_by_msg(msg)
    await bot.answer_callback_query(callback_query.id)

    if scanning_job:
        await msg.answer("Scanning is in process. Please wait!")

        doc_content = await scanning_job.scan()
        if scanning_job.scanned:
            Metrics.scanning.labels("requests").inc()
            logger.info(f"{user.mention} ({user.id}) confirmed scanning")

            await msg.answer_document(InputFile(io.BytesIO(doc_content), "document.pdf"))

            await update_scanning_job_msg(scanning_job)
            scanning_jobs.remove(scanning_job)

            await send_ads(bot, user.id)
        else:
            if doc_content == 409:
                await msg.answer("Please put the paper in the scanner.")
            else:  # Error 503 and other
                await msg.answer("Unfortunately, the scanner is currently busy. Try again in a few seconds.")
