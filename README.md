# Books Aggregator

This is a web application to scrape books from differents websites and display it in a web application to make it easy to select, filter and print (as xlsx file). 

### Prerequisites

if you want to run this app locally on your machine you need to have [python 3.*](https://www.python.org/downloads/release/python-379/) pre-installed on your OS.

### Run This project locally on your machine

After installing Python, you can follow this steps:

Clone this Repository on your machine, on your terminal/cmd.. :

```
git clone https://github.com/zerrouki95samir/booksAggr.git
```
cd to plotlyChartApi directory:

```
cd booksAggr
```

Install all the requirements packages:

```
pip install -r requirements.txt
```

Run the app:
 
```
python app.py
```

If everything goes well, you will see this line at the end of your command line!:  

```
Running on http://127.0.0.1:portNumber/ (Press CTRL+C to quit)
```

### Update the data
If you want to update the data; cd to schedulers/ folder:
```
cd schedulers
```

And run main.py file

```
python main.py
```

after the script finish the older csv file will overwrited with the new one (without any duplicates).




## Author

* **ZERROUKI SAMIR** - [zerrouki95samir](https://github.com/zerrouki95samir)