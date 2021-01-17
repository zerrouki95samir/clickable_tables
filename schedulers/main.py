import pandas as pd
from os import path
from queue import Queue
from threading import Thread
import time
import hashlib
from scrapers import (
                    elsevier as els,
                    penguin as png,
                    springer as spg,
                    ss
                )

def generate_book_id(title=None):
            new_name = ""
            for character in title:
                if character.isalnum():
                    new_name += character.lower()
            hashName = int(hashlib.sha256(new_name.encode('utf-8')).hexdigest(), 16) % 10**8
            return int(hashName)


def thread1(q):
    elsevier_data = els.go_elsevier()
    q.put(elsevier_data)

def thread2(q):
    penguin_data = png.go_penguin()
    q.put(penguin_data)

def thread3(q):
    springer_data = spg.go_springer()
    q.put(springer_data)
    
def thread4(q):
    ss_data = ss.go_ss() #40
    q.put(ss_data)
  
if __name__ == '__main__':
    result_queue = Queue()
    th1 = Thread(target=thread1, args=(result_queue,))
    th2 = Thread(target=thread2, args=(result_queue,))
    th3 = Thread(target=thread3, args=(result_queue,))
    th4 = Thread(target=thread4, args=(result_queue,))    
    
    
    # Starting threads...
    t0 = time.time()
    print("Start: %s" % time.ctime())
    th1.start()
    th2.start()
    th3.start()
    th4.start()
    
    # Waiting for threads to finish execution...
    th1.join()
    th2.join()
    th3.join()
    th4.join()

    t1 = time.time()
    print(f"{t1-t0} seconds to get all the data.")
    
    # After threads are done, we can read results from the queue.
    data = []
    while not result_queue.empty():
        result = result_queue.get()
        data.append(result)
    
    
    
    # Combine all the data 
    new_df = pd.DataFrame()
    for d in data:
        new_df = new_df.append(d, ignore_index=True)
    
    # process the new data 
    new_df['Publisher'] = new_df['website_source'].str.split('.').str[1]
    new_df['book_id'] = new_df['title'].map(lambda title: generate_book_id(title))
    
    # Open our previous excel file:
    csv_path = '../database/books.csv' 
    if path.exists(csv_path):
        books = pd.read_csv(csv_path)
    else: 
        books = pd.DataFrame()
        
    books = books.append(new_df, ignore_index=True)
    
    # Drop duplicates and keep only the old/First ones.
    books = books.drop_duplicates(subset=['book_id'], keep='first')
    books = books.reset_index(drop=True)
    # Save the result on ../database folder
    books.to_csv(csv_path, index=False)
    
    print('Process done successfully...')    








