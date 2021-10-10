import asyncio
from datetime import datetime, timedelta, timezone

import requests
import aiohttp

from bot.consts import SCANNING_JOB_LIFETIME_MINUTES


class ScanInputs:
    class Platen:
        name = "Platen"
        available_double_side = False

    class ADF:
        name = "ADF"
        available_double_side = True


class ScanningJob:
    def __init__(self):
        self.msg = None
        self.scan_input = ScanInputs.ADF
        self.double_sided = False
        self.dpi = 400

        tzinfo = timezone(timedelta(hours=3))
        self.created = datetime.now(tzinfo)

        self.scanned = False

    def generate_message_text(self):
        double_sided_text = ""
        if self.scan_input.available_double_side:
            double_sided_text = f"Scanning from both sides: <b>{'On' if self.double_sided else 'Off'}</b>\n"

        if self.scanned:
            status_msg = "<i>Scanning completed.</i>"
        else:
            time = (self.created + timedelta(minutes=SCANNING_JOB_LIFETIME_MINUTES)).strftime("%H:%M")
            status_msg = f"<i>Scanning will be cancelled in {SCANNING_JOB_LIFETIME_MINUTES} min (at {time} MSK).</i>"

        dpi_warning_msg = ""
        if self.dpi >= 600:
            dpi_warning_msg = "(Higher-resolution causes larger file size and increases scanning duration)"

        res = f"<b>Ready to scan</b>\n" \
              f"Put your documents into scanner\n\n" \
              f"<i>Parameters:</i>\n" \
              f"Input: <b>{self.scan_input.name}</b>\n" \
              f"{double_sided_text}" \
              f"Quality: <b>{self.dpi}</b> DPI {dpi_warning_msg}\n\n" \
              f"To get tutorial use /help_scan\n" \
              f"If you have some problems, use /problem_scan\n\n" \
              f"{status_msg}"
        return res

    async def scan(self):
        session = aiohttp.ClientSession()

        response = await session.post("https://10.90.109.61:9096/eSCL/ScanJobs",
                                      headers={"Content-Type": "application/xml"},
                                      data=generate_scan_xml(self.get_input_source(), self.get_duplex(), self.dpi),
                                      verify_ssl=False)

        file_url = response.headers.get("Location", None)
        if not file_url:
            return response.status

        file_response = None
        while file_response is None:
            try:
                await asyncio.sleep(1)
                file_response = await session.get(file_url + "/NextDocument", raise_for_status=True, verify_ssl=False)
            except aiohttp.ServerDisconnectedError:
                await asyncio.sleep(1)

        doc = await file_response.content.read()
        self.scanned = True

        await session.delete(file_url, verify_ssl=False)

        await session.close()

        return doc

    def get_input_source(self):
        if self.scan_input == ScanInputs.ADF:
            return "Feeder"
        else:
            return "Platen"

    def get_duplex(self):
        if self.scan_input == ScanInputs.ADF and self.double_sided:
            return "<scan:Duplex>true</scan:Duplex>"
        return ""


# kwarg = {'proxies': {"http": "http://10.90.138.234:3128", "https": "http://10.90.138.234:3128"}}
kwarg = {'proxy': "http://10.90.138.234:3128"}


def generate_scan_xml(input_source, duplex, dpi):
    print(input_source)
    res = f"""
    <?xml version="1.0" encoding="UTF-8"?>
    <scan:ScanSettings xmlns:pwg="http://www.pwg.org/schemas/2010/12/sm" 
    xmlns:scan="http://schemas.hp.com/imaging/escl/2011/05/03">
    <pwg:Version>2.63</pwg:Version>
      <pwg:ScanRegions>
        <pwg:ScanRegion>
          <pwg:Height>4205</pwg:Height>
          <pwg:Width>2551</pwg:Width>
          <pwg:XOffset>0</pwg:XOffset>
          <pwg:YOffset>0</pwg:YOffset>
        </pwg:ScanRegion>
      </pwg:ScanRegions>
      <pwg:InputSource>{input_source}</pwg:InputSource>
      {duplex}
      <scan:AdfOption>Duplex</scan:AdfOption>
      <scan:ColorMode>RGB24</scan:ColorMode>
      <scan:XResolution>{dpi}</scan:XResolution>
      <scan:YResolution>{dpi}</scan:YResolution>
      <pwg:DocumentFormat>application/pdf</pwg:DocumentFormat>
    </scan:ScanSettings>
    """
    return res
