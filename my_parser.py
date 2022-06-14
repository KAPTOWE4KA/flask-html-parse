from bs4 import BeautifulSoup
import requests as req
from sql_controller import TableController


def parse(genre=""):
    url = "https://store.steampowered.com/search/results?sort_by=Released_DESC&force_infinite=1"
    if genre!="":
        url += f"&genre={genre}"
    resp = req.get(url)
    print(f"URL: {url}")
    if resp.status_code!=200:
        return -1
    #TODO по статусу не робит - если жанр не существует он вернет все игры.
    # нужно цеплять кол-во записей и если она будет больше 105 тысяч то значит жанра не существует
    open("test.html", "w", encoding="utf-8").write(resp.text)
    return 0
    soup = BeautifulSoup(resp.text, "lxml")
    results = soup.find("div", id="search_resultsRows")
    # pages = soup.find("div", id="search_pagination_right").find_all("a")
    # max_pages = 1
    # for a in pages:
    #     max()

    games_table = TableController("steam_games.sqlite", "games")
    tags_table = TableController("steam_games.sqlite", "game_tags")
    game_2_tag_table = TableController("steam_games.sqlite", "game_to_game_tags")

    if not (games_table.test_connect() and tags_table.test_connect() and game_2_tag_table.test_connect()):
        return -2

    game_tags = []
    valute_symbol = ""
    for tag in results.find_all("a"): # searching valute simbol to use it further
        if tag.find("div", attrs={"class": "search_price"}).text.__len__() > 1 and "free" not in tag.find("div", attrs={"class": "search_price"}).text.lower():
            valute_simbol = tag.find("div", attrs={"class": "search_price"}).text.strip()[-1]
            break

    for tag in results.find_all("a"):
        print("Game link: "+tag['href'])

        tags_soup = BeautifulSoup(req.get(tag['href']).text, "lxml").find_all("a", attrs={"class": "app_tag"})
        for game_tag in tags_soup:
            if game_tag not in game_tags:
                game_tags.append(game_tag.text.strip())

        print("Game id: " + tag['data-ds-itemkey'])  # game id
        print("Game name: "+tag.find("span", attrs={"class": "title"}).text) # game name
        print("Game release date: "+tag.find("div", attrs={"class": "search_released"}).text) # release date
        if tag.find("strike"):
            print("Game discount: "+tag.find("div", attrs={"class": "search_discount"}).find("span").text)  # discount
            print("Game inst price: "+tag.find("strike").text)  # game inst price
            print("Game final price: "+tag.find("div", attrs={"class": "search_price"}).contents[3])  # game final price
        else:
            if tag.find("div", attrs={"class": "search_price"}).text.__len__() > 1 and "free" not in tag.find("div", attrs={"class": "search_price"}).text.lower():
                print("Game price: "+tag.find("div", attrs={"class": "search_price"}).text.strip())  # game final price
            else:
                print(f"Game price: 0{valute_simbol}")
        print("Game image link: "+tag.find("img")["src"])

    print("Game tags: ")
    print(game_tags)