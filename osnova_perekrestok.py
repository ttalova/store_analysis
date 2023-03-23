import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

ua = UserAgent()
list_of_categories_links = []
list_of_category_names = []
dict_of_products = dict()

headers = {'User-Agent': ua.chrome}
webside = 'https://www.perekrestok.ru/cat'
help_link = 'https://www.perekrestok.ru'

resp = requests.get(webside, headers=headers)
soup = BeautifulSoup(resp.content, 'lxml')
product_button = soup.find('main').find_all('div', {'class': 'sc-gsTCUz coCsbI'})[1].find_all('div', {
    'class': 'sc-dlfnbm jwhrZg catalog__column'})
links_of_category = [link.find('a').get('href') for link in product_button]

for link in links_of_category[2:]:
    resp_link = requests.get(help_link + link, headers=headers)
    soup_link = BeautifulSoup(resp_link.content, 'lxml')
    name_category = soup_link.find('main').find('div', {'class': 'sc-laRPJI fcDJqq'}).find_all('div', {
        'class': 'products-slider__header'})
    list_of_category_names.append([name.find('h2').text for name in name_category])
    list_of_categories_links.append([help_link + link.find('a').get('href') for link in name_category])

if __name__ == '__main__':
    for name, elem in zip(list_of_category_names, list_of_categories_links):
        for n, e in zip(name, elem):
            file = str(n) + '.txt'
            with open('C:/Users/talov/summerpractic/links_categories/' + file, 'w') as f:
                f.write(e)
