# SteveIrwin
from bs4 import BeautifulSoup
import datetime
from random import randint
from random import shuffle
import re
from time import sleep
from urllib.request import Request
from urllib.request import urlopen

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

    # This website is in pounds, i.e. GBP
    stamp['currency'] = "GBP"

    # image_urls should be a list
    images = []                    
    try:
        image_items = html.find_all("a", {"id": re.compile('_EKM_PRODUCTIMAGE_LINK_*')})
        for image_item in image_items:
            img_href = image_item.get('href')
            if img_href != '#':
                img = 'https://www.steveirwinstamps.co.uk' + img_href
                if img not in images:
                    images.append(img)
    except:
        pass
    
    condition = {}
    
    try:
        condition_items = html.select('.product-short-description table tr')
        if condition_items:
             
            for condition_item in condition_items:
                if condition_item.select('td'):
                    condition_text = condition_item.select('td')[0].get_text()
                    price = condition_item.select('td')[1].get_text()
                    price = price.replace('£','').strip()
                    condition[condition_text] = price
                    stamp['condition'] = condition.replace('\r\n\t\t\t\t','')
    except:
        pass
    
    stamp['condition'] = condition
    
    try:
        raw_text = html.select('.product-short-description')[0].get_text()
        if stamp['condition']:
            if ' Condition Price ' in raw_text:
                raw_text_parts = raw_text.split(' Condition Price ')
            else:
                raw_text_parts = raw_text.split("\r\n")
            raw_text = raw_text_parts[0]
        stamp['raw_text'] = raw_text.replace('For details on the condition categories click here.', '').strip()
    except:
        stamp['raw_text'] = None
    if stamp['raw_text']==None and stamp['title']!=None:
        stamp['raw_text']=stamp['title']

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
            item_text = item.get_text().strip()
            if 'View Items' in item_text:
                items.append(item_link)
    except: 
        pass

    shuffle(items)
    
    return items

def get_page_items_details(page_url):
    while(page_url): 
        page_items, page_url = get_page_items(page_url)
        for page_item in page_items:
            stamp = get_details(page_item)

item_dict = {'Australia':'https://www.steveirwinstamps.co.uk/australia-1-c.asp',
    'New Zealand':'https://www.steveirwinstamps.co.uk/new-zealand-2-c.asp',
    'Islands':'https://www.steveirwinstamps.co.uk/australian-territories-10-c.asp', 
    'Postal History':'https://www.steveirwinstamps.co.uk/australasian-postal-history-695-c.asp'
    }
    
print(item_dict)  

selection = input('Choose country: ')
            
category_url = item_dict[selection]
if 'steveirwinstamps.co.uk' in category_url:
    categories = get_categories(category_url)
    for category in categories:
        categories2 = get_categories(category)
        if categories2:
            for category2 in categories2:
                categories3 = get_categories(category2)
                if categories3:    
                    for category3 in categories3:
                        get_page_items_details(category3)
                else:
                    get_page_items_details(category2)
        else:
            get_page_items_details(category)