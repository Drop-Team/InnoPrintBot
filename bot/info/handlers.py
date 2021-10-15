from aiogram.types.message import ParseMode

from bot.command_tools.message_handlers import add_message_handler
from bot.metrics import Metrics
from bot.logger import logger


@add_message_handler(commands=["start"])
async def start_command(msg):
    user = msg.from_user
    Metrics.start_command.inc()
    logger.info(f"{user.mention} ({user.id}) used /start")
    answer = "Welcome! @InnoPrintBot is a bot for easy printer access in Innopolis University’s 5th floor public " \
             "printer.\n\n" \
             "You can send a file to print it, or use /scan to scan your documents." \
             "\n\n" \
             "<i>By continuing, you confirm our privacy policy /privacy</i>\n\n" \
             "<i>If something went wrong, please go to the support channel - @TessingTech</i>\n\n" \
             "<b>First, you need to sign up. Enter your Innopolis email.</b>"
    await msg.answer(answer, parse_mode=ParseMode.HTML)


@add_message_handler(commands=["help"])
async def help_command(msg):
    user = msg.from_user
    logger.info(f"{user.mention} ({user.id}) used /help")
    answer = "This is @InnoPrintBot - bot for printing on Innopolis University's 5th floor public printer.\n\n" \
             "Official info channel & support - @TessingTech\n\n" \
             "Scanning tutorial /scan_help\n" \
             "If you have problems with <b>printing</b> /problem_print\n" \
             "If you have problems with <b>scanning</b> /problem_scan\n" \
             "Privacy policy /privacy\n" \
             "Source code - <i>https://github.com/blinikar/innoprintbot</i>\n" \
             "Donate - <i>https://tinkoff.ru/cf/5vE5LgA9E2E</i>"
    await msg.answer(answer, parse_mode=ParseMode.HTML)


@add_message_handler(commands=["privacy"])
async def privacy_command(msg):
    answer = "Our full public privacy policy - <i>https://bit.ly/2Yu2L4z</i>\n\n" \
             "<i>Our privacy fundamentals:</i>\n" \
             "• We save your email address & Telegram account ID for identification & statistics\n" \
             "• We permanently save file names of your document & file metadata\n" \
             "• We temporarily (&lt60 mins) save your document’s content"
    await msg.answer(answer, parse_mode=ParseMode.HTML)


@add_message_handler(commands=["problem_print"])
async def problem_print_command(msg):
    Metrics.problem.labels("print").inc()
    answer = "Printer problems:\n\n" \
             "> Check power supply\n" \
             "> Check printer’s display for errors\n" \
             "> If <b>Paper jammed</b> -> remove jammed papers from printer -> reboot printer -> enter captcha\n" \
             "> When the printer starts you need to <b>enter a captcha</b> (follow instructions on the display)\n" \
             "> Check that your file doesn’t corrupt\n" \
             "> Check file extension, we recommend <b>using PDF format</b>. We have an automatical conversation, " \
             "but it can work badly.\n\n" \
             "<i>Support @TessingTech</i>"
    await msg.answer(answer, parse_mode=ParseMode.HTML)


@add_message_handler(commands=["problem_scan"])
async def problem_scan_command(msg):
    Metrics.problem.labels("scan").inc()
    answer = "Scanner problems:\n\n" \
             "> Check power supply\n" \
             "> When the printer starts you need to <b>enter a captcha</b> (follow instructions on the display)\n" \
             "> Check printer’s display for errors\n" \
             "> If <b>Device operating remotely</b> more than 3 minutes -> press cancel -> " \
             "open and then, close top scanner cover, it doesn’t matter which type of scan you want to use " \
             "(don’t ask why) -> you can reboot printer if that doesn't affect -> enter captcha\n\n" \
             "<i>Support @TessingTech</i>"
    await msg.answer(answer, parse_mode=ParseMode.HTML)
