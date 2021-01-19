import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import re

def scrape(stop_in_page=None):
    options = webdriver.ChromeOptions()
    # options.add_argument('--ignore-certificate-errors')
    # options.add_argument(
    #     '--user-agent="Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16D57"')
    options.add_argument('--headless')
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    page = 1
    df = pd.DataFrame()
    while True:
        print(f'Getting page {page} ...')
        url = f'https://www.springer.com/gp/product-search/discipline?disciplineId=businessmanagement&dnc=true&facet-lan=lan__en&facet-pdate=pdate__onemonth&facet-type=type__book&page={page}&returnUrl=gp%2Fbusiness-management&topic=500000%2C511000%2C511010%2C511020%2C512000%2C513000%2C513010%2C513020%2C513030%2C513040%2C513050%2C514000%2C514010%2C514020%2C514030%2C515000%2C515010%2C515020%2C515030%2C515040%2C516000%2C517000%2C517010%2C517020%2C517030%2C518000%2C519000%2C519010%2C519020%2C519030%2C519040%2C521000%2C522000%2C522010%2C522020%2C522030%2C522040%2C522050%2C522060%2C522070%2C523000%2C524000%2C524010%2C525000%2C525010%2C526000%2C526010%2C526020%2C527000%2C527010%2C527020%2C527030%2C527040%2C527050%2C527060%2C527070%2C527080%2C528000%2C600000%2C611000%2C612000%2C613000%2C613010%2C613020%2C614000%2C615000%2C616000%2C617000%2C618000%2C619000%2C621000%2C622000'
        driver.get(url)
        #WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div/form/div[2]/div[2]/div[2]/div[1]/p[3]/span[2]")))
        sleep(2)
        html = driver.page_source
        # if res.status_code == 200:
        soup = BeautifulSoup(html, 'html.parser')
        books_container = soup.find('div', {'id': 'result-list'})
        if books_container:
            for book in books_container.find_all('div', {'class': ['result-item', 'result-item-0', 'result-type-book']}):
                book_link = ''
                cover_link = ''
                title = ''
                price = ''
                contributors = ''
                pub_date= ''
                a = book.find('a')
                if a:
                    book_link = 'https://www.springer.com'+a.get('href')
                    img_tag = a.find('img')
                    if img_tag:
                        cover_link = img_tag.get('data-original')

                title_tag = book.find('h4')
                if title_tag:
                    title = title_tag.text.strip()
                p_tags = book.find('span', {'class': 'price'})
                if p_tags:
                    price = p_tags.text.strip()
                contr_tag = book.find(
                    'p', {'class': ['meta', 'contributors', 'book-contributors']})
                if contr_tag:
                    contributors = contr_tag.text.strip()
                    if ('(' in contributors) and (')' in contributors):
                        year = re.findall(r'\d+', contributors)
                        for y in year:
                            if len(y) == 4:
                                pub_date = y
                                break
                        

                df = df.append({
                    'title': title,
                    'author': contributors,
                    'price': price,
                    'book_link': book_link,
                    'cover_link': cover_link,
                    'website_source': 'https://www.springer.com/', 
                    'Publication date': pub_date
                }, ignore_index=True)
        # else:
            #print(f'Status code {res.status_code} on {url}')

        if stop_in_page:
            if page == stop_in_page:
                break
        page += 1
        #df.to_excel('springer.xlsx', index=False)

    driver.close()
    return df


def go_springer(stop_at_page=7):
    # Specify what page number that you want to stop the scraper on it
    # You can set "None" to scrape all the pages
    #stop_in_page = 15
    springer = scrape(stop_at_page)
    springer['scrape_date'] = str(datetime.today().date())
    #springer.to_excel('springer.xlsx', index=False)

    print('springer done successfully..')
    return springer
