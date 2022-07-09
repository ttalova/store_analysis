import requests
import os
import time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials

CREDENTIALS_FILE = 'perekrestok-355612-c97ad2d95599.json'  # Имя файла с закрытым ключом, вы должны подставить свое

# Читаем ключи из файла
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                               ['https://www.googleapis.com/auth/spreadsheets',
                                                                'https://www.googleapis.com/auth/drive'])

httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API

spreadsheet = service.spreadsheets().create(body={
    'properties': {'title': 'Перекресток', 'locale': 'ru_RU'},
    'sheets': [{'properties': {'sheetType': 'GRID',
                               'sheetId': 0,
                               'title': 'Цены на товары по категориям',
                               'gridProperties': {'rowCount': 1000000, 'columnCount': 10}}}]
}).execute()
spreadsheetId = '1ucSYtPRQlnbx6ZVOFicbpzru6GbYzRdEvjv8_Jt-FdI'  # сохраняем идентификатор файла
print('https://docs.google.com/spreadsheets/d/' + spreadsheetId)
# driveService = apiclient.discovery.build('drive', 'v3', http = httpAuth) # Выбираем работу с Google Drive и 3 версию API
# access = driveService.permissions().create(
#     fileId = spreadsheetId,
#     body = {'type': 'user', 'role': 'writer', 'emailAddress': 'talova0304@gmail.com'},  # Открываем доступ на редактирование
#     fields = 'id'
# ).execute()
ua = UserAgent()
headers = {'User-Agent': ua.opera}
webside = 'https://www.perekrestok.ru/cat'
help_link = 'https://www.perekrestok.ru'
list_of_name_of_categories = []
list_of_name_products = []
list_of_price_of_products = []
list_of_categories_links = []
list_of_category_names = []

for filename in os.listdir("links_categories"):
    with open(os.path.join("links_categories", filename), 'r') as f:
        list_of_categories_links.append(f.read())
        list_of_category_names.append(filename.replace('.txt', ''))


def parsing_category(categories_link):
    resp_h = requests.get(categories_link, headers=headers)
    soup_h = BeautifulSoup(resp_h.content, 'lxml')
    list_podcategories = soup_h.find('main').find('div', {'class': 'sc-laRPJI fcDJqq'}).find_all('div', {
        'class': 'catalog-content-group__list'})
    return list_podcategories


def parsing_podcategory(list_podcategories):
    list_of_every_card = [
        podcategory_1.find('div', {'class': 'sc-gsTCUz coCsbI'}).find_all('div', {'class': 'product-card__content'}) for
        podcategory_1 in list_podcategories]
    return list_of_every_card


def parcing_card(card):
    return (
        card.find('div', {'class': 'product-card-title__wrapper'}).find('div', {'class': 'product-card__title'}).text,
        card.find('div', {'class': 'product-card__control'}).find('div', {'class': 'price-new'}).text)


count = 0
for name, elem in zip(list_of_category_names, list_of_categories_links):
    first = parsing_category(elem)
    second = parsing_podcategory(first)
    for el in second:
        for card in el:
            result = parcing_card(card)
            list_of_name_of_categories.append(name)
            list_of_name_products.append(result[0])
            list_of_price_of_products.append(result[1].replace(u'\xa0₽', ''))
    count += 1
    if count == 10:
        time.sleep(40)
        count = 0

results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
    "valueInputOption": "USER_ENTERED",  # Данные воспринимаются, как вводимые пользователем (считается значение формул)
    "data": [
        {"range": f"A1:C{len(list_of_name_products)}",
         "majorDimension": "COLUMNS",  # Сначала заполнять строки, затем столбцы
         "values": [list_of_name_of_categories, list_of_name_products, list_of_price_of_products
                    # Заполняем вторую строку
                    ]}
    ]
}).execute()

if __name__ == '__main__':
    print('done')
