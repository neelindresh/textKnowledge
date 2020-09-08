import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

#driver = webdriver.Chrome()
options = webdriver.ChromeOptions()
options.add_argument('headless')

# start chrome browser
def getFromUrl(url):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    browser = webdriver.Chrome("/Users/indreshbhattacharya/Desktop/workspace/Flask_Applications/textsummery/chromedriver",options=options)

    browser.get(url)

    #driver=webdriver.PhantomJS()

    soup=BeautifulSoup(browser.page_source,"html.parser")

    #print(soup)

    browser.quit()
    title=soup.find("h1").text
    document=""
    for i in soup.findAll("p"):
        document+=i.text
    return title, document
