from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from novikovtv_parser_tenchat.parser.selenium_tenchat_parser.SeleniumTenchatParser import SeleniumTenchatParser


async def make_csv_text(web_driver_path, chrome_path, phone_number, search_query, model_api_key, max_people_count=500):
    chrome_options = Options()

    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36")

    #нужно запустить хром командой linux "google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug"
    #chrome_options.debugger_address = "127.0.0.1:9222"

    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    chrome_options.binary_location = chrome_path
    service = Service(web_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        selenium_tenchat_parser = SeleniumTenchatParser(driver, 0.1, 30)
        await selenium_tenchat_parser.enter_phone(phone_number)
        code = yield "Введите код подтверждения"
        await selenium_tenchat_parser.enter_code_and_login(code)
        await selenium_tenchat_parser.search_people(search_query)
        community_links = await selenium_tenchat_parser.get_people_links(max_people_count)
        parsed_data = await selenium_tenchat_parser.parse(community_links)

        yield SeleniumTenchatParser.get_csv_result_string(parsed_data, model_api_key)
    finally:
        driver.quit()