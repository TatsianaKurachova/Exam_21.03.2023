from bs4 import BeautifulSoup as bs
import requests
import pandas as pd

URL_FILM = "https://topnaroda.com/rating/kino/37161-top-100-filmov-vseh-vremen.html"
FILE_NAME = "movies.csv"

r = requests.get(URL_FILM)
print(r.text)

soup = bs(r.text, "html.parser")
films_names = soup.find_all('div', class_='s-right5')
for name in films_names:
    print(name.a.contents[0])

films_info = soup.find_all('ul', class_='s-info')
for name in films_names:
    print('https://topnaroda.com/rating/kino/37161-top-100-filmov-vseh-vremen.html'+name.a.contents[0])
for info in films_info:
    print(info.text)


def parse(url = URL_FILM):
    result_list = {'Название фильмы и год выпуска': [], 'Описание': [], 'О фильме': []}
    r = requests.get(url)
    soup = bs(r.text, "html.parser")
    films_names = soup.find_all('div', class_='s-right5')
    films_info = soup.find_all('ul', class_='s-info')
    for name in films_names:
        result_list['Название фильмы и год выпуска'].append(name.a.contents[0])
        result_list['Описание'].append('https://topnaroda.com/rating/kino/37161-top-100-filmov-vseh-vremen.html')
    for info in films_info:
        result_list['О фильме'].append(info.text)
    return result_list


df = pd.DataFrame(data=parse())
df.to_csv(FILE_NAME)