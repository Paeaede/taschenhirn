'''
Scraper for taschenhirn.de based on requests and beautifulsoup.

This is definitely not good style and can be adapted if anyone feels like doing so.
I copy pasted most codes from:
https://www.digitalocean.com/community/tutorials/how-to-work-with-web-data-using-requests-and-beautiful-soup-with-python-3

Also the data is currently not stored in a db or xml like structured relations but only in flat files


- a lot hardcoded stuff (e.g. page names, div + paragraph ids etc... only tested with "geografie" category
- only tables (if tablenames follow the pattern of geografie) are scraped. Additional texts not
'''

import requests
from bs4 import BeautifulSoup


def crawl_category(category_name: str):
    '''

    :param category_name: name of first subcategory in taschenhirn hierarchy (e.g. "geografie"
    :return: writes flat files into data folder with titles "category_name + subcategory".
    This can be changed in the future, however, I wanted just to test how haystack is performing

    '''
    url = 'https://www.taschenhirn.de/' + category_name + '/'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
#    print(soup.prettify())
    # create dictionary of subpages to crawl data from:
    subpages = {}
    left_menu = soup.find("ul", { "id" : "leftmenu" })
    for entry in left_menu.find_all('a', href=True):
        subpages[entry.text] = entry['href']

    # loop over subpages:
    for key, value in subpages.items():
        suburl = value
        subpage = requests.get(suburl)
        subsoup = BeautifulSoup(subpage.content, 'html.parser')

        # retrieve tables into lists:
        table_data = subsoup.find('table', {'class' : 'dataList'})
        try:
            assert table_data is not None
        except AssertionError as e:
            print(e, 'Problem with reading table under {}'.format(value))
        rows = table_data.find_all('tr')
        store = []
        row = []
        numcols = []
        key = key.strip()
        key = key.replace('&', 'und')
        key = key.replace('?', '')
        key = key.replace(' ', '_')
        with open('./data/' + category_name + '_' +key + '.txt', 'w') as f:
            for tr in rows:
                cols = tr.findAll('td')
                for td in cols:
                    try:
                        text = ''.join(td.find(text=True))
                    except Exception:
                        text = ''
                    text = text + "\n"
                    row.append(text)
                store = ''.join(row)
            f.write(store)

if __name__=='__main__':
    category_name = 'geografie'#'geografie' # geografie
    crawl_category(category_name)

