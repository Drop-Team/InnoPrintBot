import os

from bot.utils.jobs.job import jobs
from bot.utils.printing.job.job import PrintJob
from .loops_counter import LoopsCounter

loops_counter = LoopsCounter()

files_directory = os.getenv("FILES_PATH")


async def check_for_files():
    """Check all files in directory for printed documents and delete some if necessary"""

    loops_counter.count()
    if not loops_counter.check():
        return

    print_jobs_filenames = []
    for job in jobs:
        if type(job) is not PrintJob:
            continue
        job: PrintJob
        print_jobs_filenames.append(job.get_file_path().split("/")[-1])

    for filename in os.listdir(files_directory):
        if not filename.endswith(".pdf"):
            continue
        if filename in print_jobs_filenames:
            continue
        os.remove(files_directory + filename)
