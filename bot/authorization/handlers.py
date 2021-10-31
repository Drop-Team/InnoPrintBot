from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.types.message import ParseMode

from bot.command_tools.message_handlers import add_message_handler
from bot.command_tools.cooldown_lifetime import Checks, set_check, validate_cooldown, get_remain_time, validate_lifetime
from bot.users import UserStates, users, save_file
from bot.authorization import tools
from bot.logger import logger


class Keyboard:
    change_email = "Change email"
    resend_code = "Resend code"

    @classmethod
    def generate_keyboard(cls, *buttons):
        return ReplyKeyboardMarkup(resize_keyboard=True).row(*[KeyboardButton(btn_text) for btn_text in buttons])


async def send_code(bot, user_id):
    if not validate_cooldown(user_id, Checks.CodeSending):
        remain = get_remain_time(user_id, Checks.CodeSending)
        return await bot.send_message(user_id, f"You can request new code only in {remain} sec.")

    result = tools.send_mail(user_id)
    if not result:
        answer = "There was something error sending letter. Please resend your Innopolis email."
        return await bot.send_message(user_id, answer)

    set_check(user_id, Checks.CodeSending)
    save_file()

    await bot.send_message(user_id, "📧 Check your email and enter confirmation code within 10 minutes.")


@add_message_handler(user_state=UserStates.init)
async def receive_email(msg):
    user = msg.from_user
    logger.info(f"{user.mention} ({user.id}) tried to send email")

    text = msg.text
    if not text or not tools.validate_email(text):
        answer = "⚠ You have to send your Innopolis email.\n" \
                 "We will send confirmation code " \
                 "to make sure that you are a student or an employee of Innopolis University."
        return await msg.answer(answer)

    tools.set_email(user.id, text)
    users[user.id].state = UserStates.requested_code
    save_file()

    answer = f"Email {text} has been set. Now you need to confirm it.\n" \
             f"Please wait until an email with a confirmation code is sent."
    await msg.answer(answer, reply_markup=Keyboard.generate_keyboard(Keyboard.change_email, Keyboard.resend_code))

    await send_code(msg.bot, user.id)


@add_message_handler(user_state=UserStates.requested_code, text_blacklist=[Keyboard.change_email, Keyboard.resend_code])
async def receive_code(msg):
    user = msg.from_user
    logger.info(f"{user.mention} ({user.id}) tried to enter a code")

    text = msg.text
    if not text:
        return await msg.answer(f"⚠ You have to send confirmation code.")

    if not validate_cooldown(user.id, Checks.CodeAttempt):
        remain = get_remain_time(user.id, Checks.CodeAttempt)
        return await msg.answer(f"You can attempt a code again in {remain} sec.")

    if not validate_lifetime(user.id, Checks.CodeSending):
        return await msg.answer(f"⚠ Code is already inactive. You need to request it again.")

    set_check(user.id, Checks.CodeAttempt)

    if not tools.validate_code(user.id, text):
        return await msg.answer("⚠ Code is incorrect")

    users[user.id].state = UserStates.confirmed
    save_file()

    answer = "👌 Great! All ready to print your documents. You can do this by simply sending a file here.\n" \
             "Also it is possible to /scan your documents."
    await msg.answer(answer, reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)


@add_message_handler(user_state=UserStates.requested_code, text=Keyboard.change_email)
async def receive_change_email(msg):
    user = msg.from_user
    logger.info(f"{user.mention} ({user.id}) requested email changing")

    users[user.id].state = UserStates.init
    save_file()

    await msg.answer("Send new Innopolis email.", reply_markup=ReplyKeyboardRemove())


@add_message_handler(user_state=UserStates.requested_code, text=Keyboard.resend_code)
async def receive_resend_code(msg):
    user = msg.from_user
    logger.info(f"{user.mention} ({user.id}) requested code resending")

    await send_code(msg.bot, user.id)
