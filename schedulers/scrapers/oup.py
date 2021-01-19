from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime

def scrape():
    print('Start Oup scraper...')
    df = pd.DataFrame()
    url = 'https://global.oup.com/academic/category/social-sciences/business-and-management/?cc=ro&lang=en&type=listing&prevNumResPerPage=20&prevSortField=1&sortField=8&resultsPerPage=100&start=0'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}
    source = requests.get(url, headers=headers).text  
    soup = BeautifulSoup(source, 'lxml')

    book_link = ''
    cover_link = ''
    title = ''
    price = ''
    author = ''
    pub_date = ''
    table_container = soup.find('div', {'class': 'search_result_list'})
    if table_container: 
        table = table_container.find('table')
        if table:
            for book in table.find_all('tr'):
                cover_link_tag = book.find('td', {'class': 'result_image'})
                if cover_link_tag: 
                    cover_link = cover_link_tag.a.img.get('src')
                    if 'https://global.oup.com' not in cover_link: 
                        cover_link = f'https://global.oup.com{cover_link}'
                    book_link = f"https://global.oup.com{cover_link_tag.a.get('href')}"
                
                title_tag = book.find('td', {'class': 'result_biblio'})
                if title_tag: 
                    title_h2 = title_tag.find('h2')
                    if title_h2:
                         title = title_h2.text.strip()
                         book_link = f"https://global.oup.com{title_h2.a.get('href')}"
                    
                    author = title_tag.find_all('p')[3].text
                    price_tag = title_tag.find('p', {'class': 'product_price'})
                    if price_tag:
                        price = price_tag.text.strip()
                    pub_date_tag = title_tag.find_all('p')
                    for i, pubs in enumerate(pub_date_tag):
                        if i == 4:
                            pub_date = str(' '.join(pubs.text.strip().split(' ')[2:5]))
                df = df.append({
                        'title': title,
                        'author': author,
                        'price': price,
                        'book_link': book_link,
                        'cover_link': cover_link,
                        'website_source': 'https://global.oup.com/', 
                        'Publication date':pub_date
                    }, ignore_index=True)
    return df


def go_oup():
    oup = scrape()
    oup['website_source'] = 'https://global.oup.com/'
    oup['scrape_date'] = str(datetime.today().date())
    print('Oup website scraped Successfully')
    return oup
    
#df.to_excel('oup.xlsx', index=False)

