import os

import aiohttp
from aiohttp.client_exceptions import ClientConnectorError

from .options_xml import get_options_xml
from ..exceptions import ScanningException


async def scan_document(options: dict) -> bytes:
    """Scan using eSCL and return document as PDF bytes"""

    host = os.getenv("PRINTER_HOST")
    protocol = os.getenv("ESCL_SCAN_PROTOCOL")
    port = os.getenv("ESCL_SCAN_PORT")

    scan_base_url = f"{protocol}://{host}:{port}/eSCL"
    print(scan_base_url)

    try:
        document_url = await start_scanning(scan_base_url, options)
        print(document_url)
        document = await get_document_by_url(document_url)
        await delete_printer_scan_job(document_url)
    except ClientConnectorError as e:
        raise ScanningException("Scanner is not available. Try again later.")

    return document


async def start_scanning(base_url: str, options: dict) -> str:
    """Starts scanning and returns document location (url) which should be checked for file existing"""

    async with aiohttp.ClientSession() as session:
        response = await session.post(
            url=base_url + "/ScanJobs",
            headers={"Content-Type": "application/xml"},
            data=get_options_xml(options),
            verify_ssl=False,
        )

        if response.status == 503:
            raise ScanningException("Scanner is busy. Wait until the current job is completed.")

        location = response.headers.get("Location")

        if not location:
            raise ScanningException("An error occurred during the scan.")

    return location


async def get_document_by_url(document_url: str) -> bytes:
    """Get document by url after starting scanning"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url=document_url + "/NextDocument", verify_ssl=False) as response:
            return await response.read()


async def delete_printer_scan_job(document_url: str) -> None:
    """Ends scanning by sending delete request"""

    async with aiohttp.ClientSession() as session:
        await session.delete(
            url=document_url,
            verify_ssl=False,
        )
