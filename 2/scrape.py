

#from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome('/usr/bin/chromedriver',options=chrome_options)


#driver = webdriver.Chrome("/usr/bin/chromedriver")
#driver = webdriver.Chrome()

products=[] #List to store name of the product
prices=[] #List to store price of the product
ratings=[] #List to store rating of the product
driver.get("https://nominis.cef.fr/contenus/prenom/alphabetique/B.html")

content = driver.page_source
#print(content)
soup = BeautifulSoup(content)
#for a in soup.findAll( attrs={'class':'mb-1'}):
for a in soup.findAll( class_="mb-1"):
    print(a.string)
    #name=a.find('div', attrs={'class':'_3wU53n'})