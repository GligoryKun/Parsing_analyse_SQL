from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from time import sleep
from random import randint
from bs4 import BeautifulSoup as BS
import lxml
from winotify import Notification, audio
from pathlib import Path
import logging
import analysing
import storage
import re

def create_folder():
    data_folder = Path.cwd() / 'data_folder'
    log_folder = Path.cwd() / 'log_folder'
    try:
        data_folder.mkdir(exist_ok=True)
        log_folder.mkdir(exist_ok=True)
    except Exception as E:
        logging.error(E)

    return data_folder,log_folder

def notification(title, msg):
    toast = Notification(app_id='Parser', title=title, msg=msg)
    toast.set_audio(audio.Default, loop=False)
    toast.show()

data_path, log_path = create_folder()

logging.basicConfig(
    filename=log_path / 'log_file.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

notification('Parser','The parser is starting. Please wait a few minutes for the result.')

def parser():
    options =  webdriver.ChromeOptions()

    # options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument(f"--user-agent={'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0 Safari/537.36'}")

    with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) as driver:

        link_of_now_page = 'https://hh.ru/search/vacancy?text=Python&search_field=name&excluded_text=&salary=&salary=&currency_code=RUR&experience=doesNotMatter&order_by=relevance&search_period=0&items_on_page=50&L_save_area=true&hhtmFrom=vacancy_search_filter'
        data = []

        try:
            for i in range(2,16):
                driver.get(link_of_now_page)
                sleep(randint(1,2))

                last_height = driver.execute_script('return document.body.scrollHeight')
                while True:
                    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                    sleep(2)
                    new_height = driver.execute_script('return document.body.scrollHeight')
                    if last_height == new_height:
                        break
                    last_height = new_height

                WebDriverWait(driver, timeout=20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-qa="vacancy-serp__vacancy"]')))

                html = driver.page_source
                soup = BS(html, 'lxml')
                next_link_block = soup.find('a', {'data-qa':'pager-next'}) # search by next pager
                if not next_link_block: # if pager-next button is hidden, search by index in list of near pages
                    next_link_block = soup.find('a', {'data-qa': 'pager-page'}, string=str(i))
                if next_link_block:
                    link_of_now_page = 'https://hh.ru'+next_link_block['href']
                    print('ok')
                    sleep(randint(3, 5))
                else:
                    print(link_of_now_page)
                    print('no')
                    break

                logging.info(f'Page {i}')

                jobs = soup.find_all('div', {'data-qa': 'vacancy-serp__vacancy'})

                for job in jobs:
                    title_element = job.find('span', {'data-qa': 'serp-item__title-text'})
                    name = title_element.text if title_element else 'Without title'

                    salary_element = job.find(lambda tag: tag.name == 'span' and '₽' in tag.text)
                    salary = salary_element.text if salary_element else 'Not Available'
                    salary = salary.replace('\u202f', ' ').replace('\xa0', ' ')

                    company_element = job.find('span',{'data-qa' : 'vacancy-serp__vacancy-employer-text'})
                    company = company_element.text if company_element else 'Not Available'
                    company = company.replace('\u202f', ' ').replace('\xa0', ' ')

                    expirience_element = job.find('span', {'data-qa' : re.compile(r'^vacancy-serp__vacancy-work-experience')})
                    expirience = expirience_element.text if expirience_element else 'Not Available'
                    expirience = expirience.replace('\u202f', ' ').replace('\xa0', ' ')

                    link = job.find('a', {'data-qa':'serp-item__title'})['href']

                    data.append((name, salary, expirience, company, link))

        except Exception as E:
            logging.error(E)
            print('error', E)

        driver.quit()
        return data

data = parser()

file_csv = data_path / 'wacancy_csv.csv'
header = [['Title', 'Salary', 'Needed expirience', 'Company', 'Link']]

storage.save_CSV(file_csv, header, data)
storage.save_excel(data_path / 'analysing.xlsx', analysing.analyse(data)[0], analysing.analyse(data)[1] )
storage.save_SQLite(data, data_path)


notification('Parser','Done')

# by gurigorie-sama 天の命