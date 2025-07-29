import asyncio
from pprint import pprint

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import csv
import io

class SeleniumTenchatParser:
    def __init__(self, driver, min_wait_time, max_wait_time):
        self.driver = driver
        self.minimal_wait_time = min_wait_time
        self.max_wait_time = max_wait_time

    async def __click_element_when_clickable(self, element: str):
        await asyncio.sleep(self.minimal_wait_time)
        WebDriverWait(self.driver, self.max_wait_time).until(EC.element_to_be_clickable((By.XPATH, element))).click()

    async def __click_element_when_clickable_by_class_name(self, class_name: str):
        await asyncio.sleep(self.minimal_wait_time)
        WebDriverWait(self.driver, self.max_wait_time).until(
            EC.element_to_be_clickable((By.CLASS_NAME, class_name))).click()

    async def __get_element_when_located(self, element: str):
        await asyncio.sleep(self.minimal_wait_time)
        return WebDriverWait(self.driver, self.max_wait_time).until(EC.presence_of_element_located((By.XPATH, element)))

    async def __get_elements_when_located(self, element: str):
        await asyncio.sleep(self.minimal_wait_time)
        return self.driver.find_elements(By.XPATH, element)

    async def __get_element_when_located_by_class_name(self, class_name: str):
        await asyncio.sleep(self.minimal_wait_time)
        return WebDriverWait(self.driver, self.max_wait_time).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_name)))

    async def __wait_element_when_located(self, element: str):
        await asyncio.sleep(self.minimal_wait_time)
        WebDriverWait(self.driver, self.max_wait_time).until(EC.presence_of_element_located((By.XPATH, element)))

    async def __wait_element_when_located_by_classname(self, class_name: str):
        await asyncio.sleep(self.minimal_wait_time)
        WebDriverWait(self.driver, self.max_wait_time).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_name)))

    async def __wait_for_new_elements_located(self, xpath: str, previous_count: int):
        await asyncio.sleep(self.minimal_wait_time)

        def more_elements_loaded(driver):
            elements = driver.find_elements(By.XPATH, xpath)
            return elements if len(elements) > previous_count else False

        return WebDriverWait(self.driver, self.max_wait_time).until(more_elements_loaded)

    async def enter_phone(self, phone_number):
        self.driver.get("https://tenchat.ru/auth/sign-in")

        time.sleep(1)
        print('Already on tenchat.ru')
        #await self.__click_element_when_clickable("//div[@data-cy='country-code']")
        #await self.__wait_element_when_located("//ul[@data-cy='countries-list']")
        #await self.__click_element_when_clickable("//img[@src='/images/emojis/1f1ec-1f1ea.png']")
        phone_input = await self.__get_element_when_located("//input[@type='tel']")
        print('Logging in with phone number: ' + phone_number)
        phone_input.send_keys(phone_number)
#
        await self.__click_element_when_clickable("//button[@data-cy='send-auth-code']")
        await self.__wait_element_when_located("//form[@data-cy='code-digits']")
        print('Waiting for enter code')

    async def enter_code_and_login(self, code: str):
        code_input_form = await self.__get_element_when_located("//form[@data-cy='code-digits']")
        first_input = code_input_form.find_element(By.TAG_NAME, 'input')
        first_input.send_keys(code)

    async def search_people(self, query):
        await self.__click_element_when_clickable("//input[@data-cy='search-input']")
        print('Login successful')
        await self.__click_element_when_clickable("//button[@data-cy='open-search-people']")

        await self.__click_element_when_clickable("//input[@name='Россия']")
        await self.__click_element_when_clickable("//span[text()='Страна']")
        time.sleep(1)

        await self.__click_element_when_clickable("//input[@name='Москва']")
        await self.__click_element_when_clickable("//input[@name='Санкт-Петербург']")
        time.sleep(1)

        await self.__click_element_when_clickable("//span[text()=' Выбрано ']")
        city_input = await self.__get_element_when_located("//input[@placeholder='Введите город']")
        city_input.send_keys('Сочи')
        await self.__click_element_when_clickable("//span[text()='Сочи']")
        time.sleep(1)

        await self.__click_element_when_clickable("//span[text()='Город']")
        time.sleep(1)

        start_age_input = await self.__get_element_when_located("//input[@placeholder='Возраст от 14']")
        end_age_input = await self.__get_element_when_located("//input[@placeholder='Возраст до 99']")

        start_age_input.send_keys('25')
        end_age_input.send_keys('55')
        time.sleep(2)

        search_input = await self.__get_element_when_located("//input[@placeholder='Поиск по людям']")
        search_input.send_keys(query)
        time.sleep(5)
        print('Searching peoples')

    async def get_people_links(self, max_people_count=500):
        links = []

        await self.__wait_element_when_located("//div[@data-cy='search-profiles-list']")

        while True:
            people = await self.__get_elements_when_located("//div[@data-cy='user-list-item']")
            people_count = len(people)
            print('Found ' + str(people_count) + ' people')

            if people_count >= max_people_count:
                break
            else:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                try:
                    await self.__wait_element_when_located("//div[@data-cy='linear-loader']")
                    print('Getting more people')
                    await self.__wait_for_new_elements_located(
                        "//div[@data-cy='user-list-item']",
                        people_count
                    )
                except:
                    people = await self.__get_elements_when_located(
                        "//div[@data-cy='user-list-item']")
                    people_count = len(people)
                    break

        if people_count >= max_people_count:
            people = people[:max_people_count]

        print('Final people count is ' + str(len(people)))

        for community in people:
            try:
                link_element = community.find_element(By.XPATH, ".//a[@data-cy='link-username']")
                link = link_element.get_attribute("href")
                name = link_element.text
                if link and name:
                    links.append((name, link))
            except:
                continue

        return links

    @classmethod
    def extract_plain_text_and_links(cls, element) -> str:
        if isinstance(element, str):
            return element.strip()

        if element.name in ['script', 'style']:
            return ''

        text_parts = []

        if 'href' in element.attrs:
            href = element.attrs['href']
            if href.startswith('/'):
                href = 'https://tenchat.ru/' + href
            text_parts.append(href.strip())

        text_parts.append(' '.join(cls.extract_plain_text_and_links(child) for child in element.contents))

        return ' '.join(filter(None, text_parts))

    @staticmethod
    def get_type_from_description(description: str, api_key: str) -> str:
        url = "https://api.intelligence.io.solutions/api/v1/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key
        }

        data = {
            "model": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            "messages": [
                {
                    "role": "system",
                    "content": "Пользователи будут присылать тебе описание своего вида деятельности, а ты должен определить, к какой из этих групп этот вид деятельности относится: 'B2B-услуги', 'Автосервис', 'Автотовары', 'Красота', 'Медицина', 'Образование', 'Поесть', 'Продукты', 'Развлечения', 'Ремонт и стройка', 'Спецмагазины', 'Спорт', 'Товары', 'Туризм', 'Услуги'. Если вид деятельности не подходит ни к одному пункту, отвечай 'Остальное'. Твой ответ должен содержать только одно слово - тип деятельности"
                },
                {
                    "role": "user",
                    "content": description
                }
            ]
        }
        try:
            start_time = time.time()
            response_object = requests.post(url, headers=headers, json=data).json()
            answer = response_object['choices'][0]['message']['content']
            end_time = time.time()
            print(answer)
            print(f"Время выполнения запроса: {end_time - start_time:.2f} секунд")
            print(f"Израсходовано: {response_object['usage']['total_tokens']} токенов")
        except Exception as e:
            print('Не удалось получить ответ от языковой модели из-за ошибки: ' + str(e))
            pprint(response_object)
            answer = "Не определено"
        return answer

    @classmethod
    def find_data_in_html(cls, html: str, name: str, link: str):
        soup = BeautifulSoup(html, 'html.parser')

        work = ''
        company = ''
        website = ''
        description = ''

        desc_element = soup.find("div", attrs={"data-cy": "bio"})
        if desc_element:
            description = desc_element.get_text(separator=" ", strip=True)

        work_element = soup.find("a", attrs={"data-cy": "profile-position-link"})
        if work_element:
            work = work_element.get_text(separator=" ", strip=True)

        company_element = soup.find("a", class_="tc-link tracking-smallest")
        if company_element:
            company = company_element.get_text()

        website_element = soup.find("div", attrs={"data-cy": "site"})
        if website_element:
            website_link = website_element.find("a", href=True)
            if website_link:
                website = website_link.get("href")

        return {
            'name': name,
            'link': link,
            'work': work,
            'company': company,
            'description': description,
            'website': website
        }

    async def parse(self, community_links):
        parsed_data = []

        for name, link in community_links:
            self.driver.get(link)
            try:
                await self.__wait_element_when_located("//div[@data-cy='posts']")
                await self.__click_element_when_clickable("//a[@data-cy='contacts-tab']")
                await self.__wait_element_when_located("//div[@data-cy='contacts-wrapper']")
                profile = await self.__get_element_when_located("//main[@data-cy='site-main']")

                group_info_html = profile.get_attribute("innerHTML")
                print(f"HTML сохранен для профиля: {name}")
                parsed_data.append(SeleniumTenchatParser.find_data_in_html(group_info_html, name, link))
            except Exception as e:
                print(f"Не удалось сохранить HTML для профиля: {name} из за ошибки: {e}")
        return parsed_data

    @staticmethod
    def get_csv_result_string(data: list, api_key) -> str:
        output = io.StringIO()
        field_names = ['name', 'link', 'work', 'company', 'description', 'type', 'website']

        string_writer = csv.DictWriter(output, fieldnames=field_names)
        string_writer.writeheader()

        for row in data:
            row['type'] = SeleniumTenchatParser.get_type_from_description(row['description'], api_key)
            string_writer.writerow(row)

        csv_content = output.getvalue()
        output.close()
        return csv_content