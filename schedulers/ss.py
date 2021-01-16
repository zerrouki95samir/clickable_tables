import requests 
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
from datetime import datetime

def scrape(stop_in_page=None):
    from_n = 0
    page = 1
    df = pd.DataFrame()
    while True:
        print(f'Getting page {page} ...')
        sleep(2)
        url = f'https://www.simonandschuster.com/search/books/Category-Business-Economics/Available-For-Sale-Now/_/N-fh8Zpgz/Ne-pgx?Nao={from_n}'
        res = requests.get(url)
        if res.status_code == 200:
            soup = BeautifulSoup(res.content, 'html.parser')
            books_container = soup.find('div', {'id': 'search-results-container'})
            if books_container: 
                for book in books_container.find_all('article'):
                    book_link = ''
                    cover_link = ''
                    title = ''
                    price = ''
                    author = ''
                    a = book.find('a')
                    if a: 
                        book_link = a.get('href')
                        img_tag = a.find('img')
                        if img_tag: 
                            cover_link = img_tag.get('data-src')
                    div = book.find('div', {'class': 'is-clipped'})
                    if div: 
                        title_tag = div.find('a')
                        if title_tag:
                            title = title_tag.text.strip()
                        p_tags = div.find_all('p')
                        if len(p_tags)>0:
                            price = p_tags[-1].text.strip()
                            try:
                                author = p_tags[-2].text.strip()
                            except:
                                print('Author not exist.')
                                
                    df = df.append({
                            'title':title,
                            'author':author,
                            'price':price,
                            'book_link':book_link,
                            'cover_link':cover_link
                        }, ignore_index=True)
        else:
            print(f'Status code {res.status_code} on {url}')
        
        if stop_in_page: 
            if page == stop_in_page:
                break
        page+=1
        from_n+=20
    return df


if __name__ == '__main__':
    # Specify what page number that you want to stop
    # You can set "None" to scrape all the pages
    stop_in_page = 25
    ss = scrape(stop_in_page)
    ss['website_source'] = 'https://www.simonandschuster.com/'
    ss['scrape_date'] = str(datetime.today().date())
    ss.to_excel('simonandschuster.xslx', index=False)





