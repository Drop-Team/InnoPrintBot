from fastapi import Request, APIRouter
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="./app/templates")

router = APIRouter()


@router.get("/telegram/print")
async def telegram_print(request: Request):
    """Page for printing request from Telegram Web App"""

    return templates.TemplateResponse("print.html", {"request": request})


@router.get("/telegram/scan")
async def telegram_scan(request: Request):
    """Page for scanning request from Telegram Web App"""

    return templates.TemplateResponse("scan.html", {"request": request})
