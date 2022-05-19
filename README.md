# InnoPrintBot

Bot for printing and scanning on the public printer of Innopolis University on the 5th floor.

## Table of Contents

- [About](#about)
- [Used](#used)
- [Deploy](#deploy)


## About

Bot which allows to print and scan with different parameters using the Telegram messenger.

It has ready-to-use components, so it's easy to add functionality.

## Used

- [AIOGram](https://github.com/aiogram/aiogram) as framework for Telegram Bot API
- [FastAPI](https://github.com/tiangolo/fastapi) as Web framework and [uvicorn](https://github.com/encode/uvicorn) for running it 
- LibreOffice:
  - [unoserver](https://github.com/unoconv/unoserver) for converting documents to PDF using LibreOffice
- [PyPDF4](https://github.com/claird/PyPDF4) for reading PDF files
- Apple CUPS (for printing):
  - [pycups](https://github.com/OpenPrinting/pycups) for interaction with CUPS
  - [pycups-notify](https://github.com/anxuae/pycups-notify) for receiving notifications about the status of a print job
  - [Docker image](https://hub.docker.com/r/ydkn/cups) for deployment
- eSCL protocol for scanning

## Deploy

### Environment

1. Rename [.env-example](https://github.com/Drop-Team/InnoPrintBot/blob/main/.env-example) to `.env`.
2. Edit it

### Printer driver

It is used by CUPS

Edit [Printer.ppd](https://github.com/Drop-Team/InnoPrintBot/blob/main/Bot/data/Printer.ppd) if necessary<br>
Now it contains drivers for "Kyocera ECOSYS M3645dn"

### Docker

To run use Docker:

```bash
docker-compose build
docker-compose -d up  # -d to run in background 
docker-compose ps
```