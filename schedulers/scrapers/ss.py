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

def get_pub_date(link):
    print(link)
    pub_date = ''
    try:
        res = requests.get('https://www.simonandschuster.com/books/Ladies-Get-Paid/Claire-Wasserman/9781982126902')
        if res.status_code == 200:
            soup = BeautifulSoup(res.content, 'html.parser')
            ul = soup.find('ul', {'class': 'with-margin-bottom-small'})
            if ul: 
                for li in ul.find_all('li'):
                    if 'Publisher' in li.text:
                        if '(' in li.text and ')' in li.text:
                            pub_date = li.text.split('(')[1].split(')')[0]
        sleep(1)
    except:
        print('Something went wrong with ss dates')
    
    return pub_date


def go_ss(stop_at_page=40):
    # Specify what page number that you want to stop
    # You can set "None" to scrape all the pages
    #stop_in_page = 40
    ss = scrape(stop_at_page)
    ss['Publication date'] = ss['book_link'].map(lambda x:get_pub_date(x))
    ss['website_source'] = 'https://www.simonandschuster.com/'
    ss['scrape_date'] = str(datetime.today().date())
    print('SS done successfully..')
    return ss
    #ss.to_excel('simonandschuster.xslx', index=False)





