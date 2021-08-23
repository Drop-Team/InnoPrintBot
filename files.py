from datetime import datetime
import subprocess
import os


MAX_FILE_SIZE = 64 * 1024 * 1024
DELETE_FILES_IN = 10
FILES_PATH = "printed_files/"


async def download_file(bot, doc):
    doc_id = doc.file_id
    doc_size = doc.file_size
    if doc_size > MAX_FILE_SIZE:
        return

    try:
        extension = "." + doc.file_name.split(".")[-1]
    except IndexError:
        extension = ""

    file_name = datetime.now().strftime("%Y%m%d-%H%M%S-%f") + extension
    file_path = FILES_PATH + file_name

    await bot.download_file_by_id(doc_id, file_path)
    return file_path


def print_file(file_path):
    subprocess.run(["lp", "botsrv/innoprintbot/printed_files/*", "-d", "5Fprinter", file_path])
    # print("print testing...")


async def check_files():
    now = datetime.now()
    for fn in os.listdir(FILES_PATH):
        if fn == ".keep":
            continue
        dt_str = fn.split(".")[0] if "." in fn else fn
        dt = datetime.strptime(dt_str, "%Y%m%d-%H%M%S-%f")
        if int((now - dt).total_seconds()) // 60 >= DELETE_FILES_IN:
            print("nice")
            os.remove(FILES_PATH + fn)
