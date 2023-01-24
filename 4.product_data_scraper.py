import csv
import os

from selectolax.parser import HTMLParser
import pandas as pd


path = "./products_pages"
csv_file_name = 'ozon.csv'

# CREATE CSV FILE IF NOT EXISTS
def create_csv(csv_file_name, order):
    with open(csv_file_name, 'w', encoding='utf-8', newline='') as file:
        csv.DictWriter(file, fieldnames=order).writeheader()

# WRITE DATA TO CSV FILE
def write_csv(csv_file_name, data):
    with open(csv_file_name, 'a', encoding='utf-8', newline='') as file:
        csv.DictWriter(file, fieldnames=list(data)).writerow(data)

# GET ALL DATA FROM SAVED PRODUCT PAGES TO CSV
def get_data(page):
    tree = HTMLParser(page)
    sku = tree.css_first('.t0m.m1t').css_first('span').text().split(' ')[-1]
    print(sku)
    title = tree.css_first('.rn7').text()
    print(title)
    data = {'name': 'Имя товара', 'value': title}
    write_csv(csv_file_name, data)
    brand = tree.css('.ne4')[-1].text()
    print(brand)
    category = tree.css('.e3m')
    category_text = ''
    for i in category:
        category_text += i.text()+"/"
    print(category_text)
    data = {'name': 'Товарная группа', 'value': category_text}
    write_csv(csv_file_name, data)
    params_table = tree.css_first('#section-characteristics').css('.v3l')
    for row in params_table:
        name = row.css_first('.v2l').text().strip()
        value = row.css_first('.lv3').text().strip()
        if 'Артикул' in name:
            sku = value
        if 'Бренд' in name:
            brand = value
        data = {'name': name, 'value': value}
        print(data)
        write_csv(csv_file_name, data)

    data = {'name': 'Бренд', 'value': brand}
    write_csv(csv_file_name, data)
    data = {'name': 'SKU(ID)', 'value': sku}
    write_csv(csv_file_name, data)
    for x in range(0, 2):
        data = {'=': '='}
        write_csv(csv_file_name, data)


def main():
    order = ['name', 'value']
    create_csv(csv_file_name, order)

    for root, subdirectories, files in os.walk(path):
        for file in files:
            print(file)
            if not 'finished_products' in file and not 'products_urls' in file:
                with open(os.path.join(root, file), 'r', encoding='utf-8') as file:
                    page = file.read()
                    get_data(page)


if __name__ == '__main__':
    main()