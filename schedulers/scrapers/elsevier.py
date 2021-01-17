import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
from datetime import datetime

def scrape(stop_in_page=None):
    page = 1
    df = pd.DataFrame()
    while True:
        print(f'Getting page {page} ...')
        sleep(2)
        url = f'https://www.elsevier.com/search-results?labels=books&sort=document.published-desc&publication-year=2021&publication-year=2020&subject-0=27382&page={page}'
        res = requests.get(url)
        if res.status_code == 200:
            soup = BeautifulSoup(res.content, 'html.parser')
            books_container = soup.find(
                'div', {'class': 'search-result-items'})
            if books_container:
                for book in books_container.find_all('article'):
                    book_link = ''
                    cover_link = ''
                    title = ''
                    paperback = ''
                    author = ''
                    h2 = book.find('h2')
                    if h2:
                        book_link = h2.a.get('href')
                        title = h2.text.strip()
                    img_tag = book.find('img')
                    if img_tag:
                        cover_link = img_tag.get('src')
                    author_tag = book.find(
                        'span', {'class': 'book-result-authors'})
                    if author_tag:
                        author = author_tag.text.strip()

                    paperback_tag = book.find(
                        'div', {'class': 'result-detail-list-item'})
                    if paperback_tag:
                        dd = paperback_tag.find('dd')
                        if dd:
                            paperback = dd.text.strip()

                    df = df.append({
                        'title': title,
                        'author': author,
                        'paperback': paperback,
                        'book_link': book_link,
                        'cover_link': cover_link
                    }, ignore_index=True)
        else:
            print(f'Status code {res.status_code} on {url}')

        if stop_in_page:
            if page == stop_in_page:
                break
        page += 1
    return df


def get_price(data, country='PT'):
    def price_of(pb):
        print(f'Getting {pb} price...')
        if pb.strip() == '':
            return ''
        else:
            url = f'https://search-app.prod.ecommerce.elsevier.com/api/book-pricing/{pb}/{country}'
            r = requests.get(url)
            sleep(1)
            if r.status_code == 200:
                r_json = r.json()
                return f"{r_json['formats'][0]['originalPrice'].get('symbol')}{r_json['formats'][0]['originalPrice'].get('amount')}"
            else:
                return ''

    data['price'] = data['paperback'].map(lambda paperback: price_of(paperback))
    return data


def go_elsevier(stop_at_page=4):
    # Specify what page number that you want to stop the scraper on it
    # You can set "None" to scrape all the pages
    #stop_in_page = 4
    elsevier = scrape(stop_at_page)
    elsevier = get_price(elsevier)
    elsevier = elsevier.drop(['paperback'], axis=1)
    elsevier['website_source'] = 'https://www.elsevier.com/'
    elsevier['scrape_date'] = str(datetime.today().date())
    print('elsevier done successfully..')
    return elsevier
    
   #elsevier.to_excel('elsevier.xlsx', index=False)


