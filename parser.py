from bs4 import BeautifulSoup
import requests as req

resp = req.get("https://store.steampowered.com/search/results?sort_by=Released_DESC&force_infinite=1"
               "&tags=19%2C492"
               "&genre=action"
               "&page=2")

soup = BeautifulSoup(resp.text, "lxml")

results = soup.find("div", id="search_resultsRows")

for tag in results.find_all("a"):
    print(tag.find("span", attrs={"class": "title"}).text) # game name
    print(tag.find("div", attrs={"class": "search_released"}).text) # release date
    if tag.find("strike"):
        print(tag.find("div", attrs={"class": "search_discount"}).find("span").text)  # discount
        print(tag.find("strike").text)  # game inst price
        print(tag.find("div", attrs={"class": "search_price"}).contents[3])  # game final price
    else:
        print(tag.find("div", attrs={"class": "search_price"}).text.strip())  # game final price
    print(tag.find("img")["src"])
    #print(tag)
    #break