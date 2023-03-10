from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import time
import random
import requests
import threading
import concurrent.futures

from bs4 import BeautifulSoup
from fake_useragent import UserAgent


useragent = UserAgent()


# WRITE HTML CONTENT TO FILE
def html_write(html: str, file_name: str) -> None:
    with open(f'products_pages/{file_name}.html', 'w', encoding='utf-8') as file:
        file.write(html)
        file.close()
    print(f'{file_name}.html записан')

# GET REQUIRED PRODUCT LINKS
def products_links_get() -> list[str]:
    with open('products_pages/products_urls.csv', 'r', encoding='utf-8') as file:
        products_urls = file.read().strip().split('\n')
        return products_urls


# SAVE FINISHED PAGES TO FILE
def done_page_write(product_page: str) -> None:
    with open('products_pages/finished_products.txt', 'a', encoding='utf-8') as file:
        file.write(product_page+'\n')
        file.close()


# PARS PROXIES LIST
def ip_select() -> list[str]:
    proxy_list_update()
    time.sleep(10)
    with open('checked_proxies.txt', 'r', encoding='utf-8') as file:
        proxy_list = file.read().strip().split('\n')
        print(proxy_list)
    return proxy_list


# GET ALL REQUIRED DATA FROM PAGES
def start(proxy_list: list[str], product_page: str) -> None:
    file_name = product_page.replace('/', '').replace('?', '').replace('.', '')[17:]
    print('Try page ', product_page)
    proxy = proxy_list[0]
    print('Try proxy: ', proxy)
    options = Options()
    options.add_argument(f"user-agent={useragent.random}")
    options.add_argument(f"--proxy-server={proxy}")
    driver = webdriver.Chrome(chrome_options=options)
    try:
        driver.get(product_page)
        check_element = None
        try:
            check_element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "section-characteristics")))
            html = driver.page_source
            html_write(html, file_name)
            print("Get HTML")
        except:
            html = driver.page_source
            if 'ERR_PROXY_CONNECTION_FAILED' or 'ConnectTimeout' or 'id="challenge-running"' or 'Что-то пошло не так' or 'Подозрительная активность' or 'ERR_TIMED_OUT' in html:
                raise NameError('ERR_PROXY_CONNECTION_FAILED')
            print('No title on page found')
            if 'class="c7"' in str(html):
                raise NameError('Not found', product_page)
            else:
                print('Try again')
                raise NameError('Cant open page by proxy')
        time.sleep(5)
    except OSError as e:
        if 'ProxyError' or 'ConnectTimeout' or 'ERR_PROXY_CONNECTION_FAILED' in str(e):
            if len(proxy_list) != 1:
                print('Proxy dont work, try next')
                start(proxy_list, product_page)
            else:
                print('No working proxy, pars new ones')
                proxy_list = ip_select()
                start(proxy_list, product_page)
        if 'NameError' in str(type(e)):
            driver.close()
            raise NameError
        else:
            print(type(e).__name__, e.args)
            driver.close()
            raise NameError('ProxyError')


def main(products_urls: list[str], proxy_list: list[str]) -> None:
    proxy_tries = 0
    file_name = 'o'
    for product_page in products_urls:
        success = 'No'
        while success != 'Yes':
            success = 'No'
            try:
                start(proxy_list, product_page)
                done_page_write(product_page)
                time.sleep(random.randint(1, 10))
                proxy_tries = 0
                success = 'Yes'
            except Exception as e:
                print('Тут ошибка: ', e)
                proxy = proxy_list[0]
                proxy_tries += 1
                print('Попытка',proxy_tries,"/3")
                time.sleep(random.randint(1,5))
                if proxy_tries >= 3:
                    proxy_list.remove(proxy)
                    print('Прокси удален, осталось', len(proxy_list))
                    proxy_tries = 0


# PROXY PARSER
def proxy_list_update() -> None:
    def site_proxies_scrap(url: str) -> None:
        r = requests.get(url)
        print('подключаемся к странице с ip', url)
        soup = BeautifulSoup(r.content, features="html.parser")
        text_field = soup.find('textarea', class_="form-control").text
        ls = text_field.split("\n")
        ls_1 = ls[3:-1]
        with open("unchecked_proxies.txt", 'a', encoding="utf-8") as file:
            for i in ls_1:
                file.write(i + "\n")
            file.close()

    def doubler(proxy):
        with open('checked_proxies.txt', 'a', encoding='utf-8') as file:
            try:
                page = requests.get('https://ipecho.net/plain', timeout=3, proxies={"http": proxy, "https": proxy})
                file.write(proxy + '\n')
                print('Status OK: ', proxy)
            except OSError as e:
                pass
                print('Dont work:', proxy)
                # print(type(e).__name__, e.args, proxy)


    with open('checked_proxies.txt', 'w', encoding='utf-8') as file:
        file.close()


    with open('unchecked_proxies.txt', 'w', encoding='utf-8') as file:
        file.close()
    site_proxies_scrap("https://www.sslproxies.org/")
    site_proxies_scrap("https://free-proxy-list.net/#list")
    site_proxies_scrap("https://free-proxy-list.net/anonymous-proxy.html")


    with open('unchecked_proxies.txt', 'r', encoding='utf-8') as file:
        proxies = file.read().split("\n")
        file.close()
    for proxy in proxies:
        try:
            my_thread = threading.Thread(target=doubler, args=(proxy,))
            my_thread.start()
        except:
            time.sleep(3)
            my_thread = threading.Thread(target=doubler, args=(proxy,))
            my_thread.start()


if __name__ == '__main__':
    products_urls = products_links_get()
    proxy_list = ip_select()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(main, (products_urls, proxy_list))