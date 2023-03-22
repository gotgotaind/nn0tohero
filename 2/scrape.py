

from selenium import webdriver
from BeautifulSoup import BeautifulSoup
import pandas as pd

#driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
driver = webdriver.Chrome()

products=[] #List to store name of the product
prices=[] #List to store price of the product
ratings=[] #List to store rating of the product
driver.get("https://nominis.cef.fr/contenus/prenom/alphabetique/B.html")

content = driver.page_source
soup = BeautifulSoup(content)
for a in soup.findAll('a',href=True, attrs={'class':'_31qSD5'}):
    name=a.find('div', attrs={'class':'_3wU53n'})