import datetime
from random import randint, shuffle
from time import sleep
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import re

def get_html(url):
    html_content = ''
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'}) #hdr)
        html_page = urlopen(req).read()
        html_content = BeautifulSoup(html_page, "html.parser")
    except: 
        pass
        
    return html_content

def get_details(url):
    
    stamp = {}
    try:
        html = get_html(url)
    except:
        return stamp

    try:
        price = html.select('#_EKM_PRODUCTPRICE')[0].get_text()
        stamp['price'] = price
    except: 
        stamp['price'] = None

    try:
        title = html.select('.right-content-area h1')[0].get_text()
        stamp['title'] = title
    except:
        stamp['title'] = None

    try:
        category = ''
        category_counter = 0
        category_items = html.select('.breadcrumb span a') 
        for category_item in category_items:
            category_counter = category_counter + 1
            category_text = category_item.get_text().strip()
            if ('Home' not in category_text) and ('Back' not in category_text) and (category_counter > 2):
                if category:
                    category = category + ' > '
                category = category + category_text 
        stamp['category'] = category
    except:
        stamp['category'] = None

    try:
        raw_text = html.select('.product-short-description')[0].get_text()
        stamp['raw_text'] = raw_text.strip()
    except:
        stamp['raw_text'] = None

    # This website is in pounds, i.e. GBP
    stamp['currency'] = "GBP"

    # image_urls should be a list
    images = []                    
    try:
        image_items = html.find_all("a", {"id" : re.compile('_EKM_PRODUCTIMAGE_LINK_*')})
        for image_item in image_items:
            img_href = image_item.get('href')
            if img_href != '#':
                img = 'https://www.steveirwinstamps.co.uk' + img_href
                if img not in images:
                    images.append(img)
    except:
        pass
    
    stamp['image_urls'] = images 

    # scrape date in format YYYY-MM-DD
    scrape_date = datetime.date.today().strftime('%Y-%m-%d')
    stamp['scrape_date'] = scrape_date

    stamp['url'] = url
    print(stamp)
    print('+++++++++++++')
    sleep(randint(25, 65))
    return stamp

def get_page_items(url):

    items = []
    next_url = ''

    try:
        html = get_html(url)
    except:
        return items, next_url

    try:
        for item in html.select('.viewitems-button a'):
            item_link = 'https://www.steveirwinstamps.co.uk/' + item.get('href').replace('&amp;', '&')
            items.append(item_link)
    except:
        pass

    try:
        next_items = html.select('#nav_btm a')
        for next_item in next_items:
            next_item_text = next_item.get_text().strip()
            if 'Next' in next_item_text:
                next_url = 'https://www.steveirwinstamps.co.uk/' + next_item.get('href')
                break
    except:
        pass
    
    shuffle(list(set(items)))
    
    return items, next_url

def get_categories(category_url):
    
    items = []

    try:
        html = get_html(category_url)
    except:
        return items

    try:
        for item in html.select('.category-item .viewitems-button a'):
            item_link = 'https://www.steveirwinstamps.co.uk/' + item.get('href')
            items.append(item_link)
    except: 
        pass

    shuffle(items)
    return items
        
item_dict = {'Australia':'https://www.steveirwinstamps.co.uk/australia-1-c.asp',
    'New Zealand':'https://www.steveirwinstamps.co.uk/new-zealand-2-c.asp',
    'Islands':'https://www.steveirwinstamps.co.uk/australian-territories-10-c.asp' 
    }
    
print(item_dict)  

selection = input('Choose country: ')
            
category_url = item_dict[selection]
categories = get_categories(category_url)
for category in categories:
    categories2 = get_categories(category)
    for category2 in categories2:
        categories3 = get_categories(category2)
        for category3 in categories3:
            page_url = category3
            while(page_url): 
                page_items, page_url = get_page_items(page_url)
                for page_item in page_items:
                    stamp = get_details(page_item)