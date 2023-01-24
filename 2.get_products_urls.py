from bs4 import BeautifulSoup
import os

path = "./category_pages"


# SAVE PRODUCT URL TO FILE
def url_writer(url):
    with open('products_pages/products_urls.csv', 'a', encoding='utf-8') as file:
        file.write("https://ozon.by"+ url+'\n')
        file.close()

# GET ALL PRODUCT URLS FROM PAGES
def urls_get(root: str, file: str) -> None:
    with open(os.path.join(root, file), 'r', encoding='utf-8') as data:
        soup = BeautifulSoup(data.read(), features='html.parser')
        products = soup.find_all('a', class_='m9k tile-hover-target')
        for product in products:
            url_writer(url = product.get('href'))
            print(product.get('href'))


def main() -> None:
    with open('products_pages/products_urls.csv', 'w', encoding='utf-8') as file:
        file.close()
    for root, subdirectories, files in os.walk(path):
        for file in files:
            urls_get(root, file)


if __name__ == '__main__':
    main()