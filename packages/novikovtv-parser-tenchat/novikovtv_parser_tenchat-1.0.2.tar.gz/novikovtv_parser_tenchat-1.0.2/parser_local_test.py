import asyncio
import os
from dotenv import load_dotenv

from novikovtv_parser_tenchat.parser.main import make_csv_text

load_dotenv()
async def do_parse():
    login = os.getenv("LOGIN")
    max_communities = int(os.getenv("MAX_COMMUNITIES"))
    web_driver_path = os.getenv("WEB_DRIVER_PATH")
    chrome_path = os.getenv("CHROME_PATH")
    search_query = 'Компания'

    task = make_csv_text(
        web_driver_path,
        chrome_path,
        login,
        search_query,
        max_communities
    )

    await task.asend(None)
    code = input("Введите код из SMS: ")
    csv_text = await task.asend(code)

    print(csv_text)

asyncio.run(do_parse())