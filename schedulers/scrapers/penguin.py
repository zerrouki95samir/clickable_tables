import requests 
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
from datetime import datetime

def scrape(start, get_n):
    url = f'https://www.penguinrandomhouse.com/ajaxc/categories/books/?from={start}&to={get_n}&contentId=business&elClass=book&dataType=html&catFilter=new-releases&sortType=frontlistiest_onsale'
    df = pd.DataFrame()
    res = requests.get(url)
    if res.status_code == 200:
        soup = BeautifulSoup(res.content, 'html.parser')
        books = soup.find_all('div', {'class': 'book'})
        for book in books: 
            cover_link = ''
            book_link = ''
            title = ''
            author = ''
            img_a = book.find('div', {'class': 'img'})
            if img_a:
                a = img_a.find('a')
                if a: 
                    book_link = f"https://www.penguinrandomhouse.com{a.get('href')}"
                    img = a.find('img')
                    if img: 
                        cover_link = img.get('src')
            title_tag = book.find('div', {'class': 'title'})
            if title_tag:
                title = title_tag.text.strip()
            
            author_tag = book.find('div', {'class': 'contributor'})
            if author_tag:
                author = author_tag.text.strip()
            
            df = df.append({
                    'title': title, 
                    'author': author,
                    'book_link': book_link,
                    'cover_link': cover_link
                }, ignore_index=True)
        
    else:
        print(f'Status code {res.status_code} on {url}')
        
    return df

def get_price(book_link):
    print(f'{book_link}')
    price = ''
    pub_date = ''
    res = requests.get(book_link)
    if res.status_code == 200:
        sleep(1.5)
        soup = BeautifulSoup(res.content, 'html.parser')
        price_tag = soup.find('span', {'class': 'price'})
        if price_tag:
            price = price_tag.text.strip()
        
        pub_date_tag = soup.find('p', {'class': 'title-details'})
        if pub_date_tag:
            date_tag = pub_date_tag.find('span', {'class': 'ws-nw'})
            if date_tag: 
                pub_date = date_tag.text.strip()
    
    return price, pub_date

def go_penguin():
    start = 0
    get_n = 150
    penguin = pd.DataFrame()
    while True: 
        print(f'Getting from {start} --- {get_n} ... ')
        sub_df = scrape(start, get_n)
        penguin = penguin.append(sub_df, ignore_index=True)
        if len(sub_df) < get_n:
            break
        start += get_n

    penguin['price'], penguin['Publication date'] = zip(*penguin['book_link'].map(get_price))
    # Save the file as excel file:
    penguin['website_source'] = 'https://www.penguinrandomhouse.com/'
    penguin['scrape_date'] = str(datetime.today().date())
    #penguin.to_excel('penguin.xlsx', index=False)
    print('penguin done successfully..')
    return penguin


                
        
   





