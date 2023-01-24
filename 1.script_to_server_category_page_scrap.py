from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

import time
import os
import concurrent.futures
import re


# WRITE HTML CONTENT TO FILES
def html_write(products: list[BeautifulSoup], file_name: str) -> None:
    if not os.path.exists('category_pages'):
        os.mkdir('category_pages')
    with open(f'category_pages/{file_name}.csv', 'w', encoding='utf-8') as file:
        for link in products:
            url = link.get('href')
            print(url)
            file.write("https://ozon.by"+ url+'\n')
        file.close()
    print(f'category_pages/{file_name}.csv записан')


# GET LINKS TO REQUIRED CATEGORIES
def category_links_get() -> list[str]:
    with open('category_pages_short_toys.csv', 'r', encoding='utf-8') as file:
        category_urls = file.read().strip().split('\n')
        return category_urls


def start(category_page: str) -> None:
    file_name = category_page.split('https://ozon.by/')[1].replace('/', '+').replace('?', '+').replace('.', '+')
    options = Options()
    options.add_argument("--window-size=1280,720")
    prefs = {'profile.default_content_setting_values': {'images': 2}}
    options.add_experimental_option('prefs', prefs)
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_options=options)
    try:
        driver.get(category_page)
        check_element = None
        try:
            check_element = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "q1k.tile-hover-target")))
            html = driver.page_source
            soup = BeautifulSoup(html, features='html.parser')
            products = soup.find_all('a', class_='q1k tile-hover-target')
            # print(products)
            try:
                html_write(products, file_name)
            except Exception as e:
                print('Cant get product link:', category_page)
            # print("HTML получен")
        except Exception as e:
            print('No product cards on page')
            print(e)
            html = driver.page_source
            if 'class="ala0"' in str(html):
                raise NameError('Finish page')
            print('No elements are available, try again')
            time.sleep(5)
            if 'ERR_PROXY_CONNECTION_FAILED' or 'ConnectTimeout' or 'id="challenge-running"' or 'Что-то пошло не так' or 'Подозрительная активность' or 'ERR_TIMED_OUT' in html:
                raise NameError('Cant connect with proxy')
            start(category_page)
    except OSError as e:
        if 'ProxyError' or 'ERR_PROXY_CONNECTION_FAILED' in str(e):
                start(category_page)
        if 'NameError' in str(type(e)):
            driver.close()
            raise NameError
        else:
            print(type(e).__name__, e.args)
            driver.close()
            raise NameError('ProxyError')


def main(category_pages: list[str]) -> None:
    for category_page in category_pages:
        i = 2
        file_name = '0'
        finish_page = False
        while i <= 100 and finish_page == False:
            finish_page = False
            success = 'No'
            while success != 'Yes':
                success = 'No'
                with open('finished_pages.csv', 'r', encoding='utf-8') as finish_file:
                    finished_pages = finish_file.read()
                    finish_file.close()
                tries = 0
                try:
                    if not category_page in finished_pages:
                        print('Try page ', category_page)
                        with open('finished_pages.csv', 'a', encoding='utf-8') as file:
                            start(category_page, file_name)
                            file.write(category_page + '\n')
                            file.close()
                        category_page = re.sub(r'page=(\d+)', f'page={i}', category_page)
                        file_name = category_page
                        i+=1
                        success = 'Yes'
                    else:
                        print("Page already was parsed: ", category_page)
                        category_page = re.sub(r'page=(\d+)', f'page={i}', category_page)
                        i += 1
                        success = 'Yes'
                except Exception as e:
                    print('Error', e)
                    if not 'Finish page' in str(e):
                        tries += 1
                        if tries >= 5:
                            print('Too much retries: ', category_page)
                            finish_page = True
                            success = 'Yes'
                        else:
                            print('Try ', tries, '/5')
                    else:
                        print('Finished page')
                        finish_page = True
                        success = 'Yes'


def parser_start():
    open('finished_pages.csv', 'a').close()
    category_urls = category_links_get()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(main, category_urls)


if __name__ == '__main__':
    parser_start()