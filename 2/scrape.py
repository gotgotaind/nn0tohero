#from selenium import webdriver
import string
import time

from bs4 import BeautifulSoup
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome('/usr/bin/chromedriver',options=chrome_options)

output="prenoms.txt"

print(string.ascii_uppercase)
#driver = webdriver.Chrome("/usr/bin/chromedriver")
#driver = webdriver.Chrome()

products=[] #List to store name of the product
prices=[] #List to store price of the product
ratings=[] #List to store rating of the product
for letter in string.ascii_uppercase:
    page=0
    stop=False
    with open(output, "a") as f:
        while( not stop ):
            if( page == 0 ):
                suffix=''
            else:
                suffix="-"+str(page)
            url="https://nominis.cef.fr/contenus/prenom/alphabetique/"+letter+suffix+".html"
            print(f'scraping {url}')
            driver.get(url)

            content = driver.page_source
            #print(content)
            soup = BeautifulSoup(content,features="html.parser")
            #for a in soup.findAll( attrs={'class':'mb-1'}):
            found=0
            for a in soup.findAll( class_="mb-1"):
                print(a.string,file=f)
                found=found+1
                #name=a.find('div', attrs={'class':'_3wU53n'})
            if( found == 0 ):
                stop=True
            time.sleep(1)
            page=page+1