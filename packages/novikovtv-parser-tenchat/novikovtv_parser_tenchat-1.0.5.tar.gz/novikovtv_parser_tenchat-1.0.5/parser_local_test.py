import asyncio
import os
from dotenv import load_dotenv

from novikovtv_parser_tenchat.parser.main import make_csv_text

load_dotenv()
async def do_parse():
    phone = os.getenv("PHONE")
    max_people_count = int(os.getenv("MAX_PEOPLE_COUNT"))
    web_driver_path = os.getenv("WEB_DRIVER_PATH")
    chrome_path = os.getenv("CHROME_PATH")
    model_api_key = os.getenv("MODEL_API_KEY")
    search_query = 'Компания'

    task = make_csv_text(
        web_driver_path,
        chrome_path,
        phone,
        search_query,
        model_api_key,
        max_people_count
    )

    await task.asend(None)
    code = input("Введите код из SMS: ")
    csv_text = await task.asend(code)

    print(csv_text)

asyncio.run(do_parse())