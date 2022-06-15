from bs4 import BeautifulSoup
import requests as req
from sql_controller import TableController
from class_game import Game


def parse(genre=""):
    url = "https://store.steampowered.com/search/results?sort_by=Released_DESC&force_infinite=1"
    if genre!="":
        url += f"&genre={genre}"
    resp = req.get(url)
    print(f"URL: {url}")
    soup = BeautifulSoup(resp.text, "lxml")
    results = soup.find("div", id="search_resultsRows")
    # pages = soup.find("div", id="search_pagination_right").find_all("a")
    # max_pages = 1
    # for a in pages:
    #     max()
    result_count = int(soup.find("div", id="search_results_filtered_warning").find_next("div").text.split(" ")[0].replace(",", ""))
    print(result_count)
    if result_count > 100000:  # if games more than 100000 then genre is not exist
        return -1
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

    GAMES = []
    for tag in results.find_all("a"):
        temp_game = Game()
        print("Game link: "+tag['href'])
        temp_game.link = tag['href']
        tags_soup = BeautifulSoup(req.get(tag['href']).text, "lxml").find_all("a", attrs={"class": "app_tag"})
        for game_tag in tags_soup:
            if game_tag not in game_tags:
                game_tags.append(game_tag.text.strip())
        temp_game.tags = game_tags
        print("Game id: " + tag['data-ds-itemkey'])  # game id
        temp_game.id = int(tag['data-ds-itemkey'].replace("App_", ""))
        print("Game name: "+tag.find("span", attrs={"class": "title"}).text) # game name
        temp_game.name = tag.find("span", attrs={"class": "title"}).text
        print("Game release date: "+tag.find("div", attrs={"class": "search_released"}).text) # release date
        temp_game.release_date = tag.find("div", attrs={"class": "search_released"}).text
        if tag.find("strike"):
            print("Game discount: "+tag.find("div", attrs={"class": "search_discount"}).find("span").text)  # discount
            temp_game.discount = int(tag.find("div", attrs={"class": "search_discount"}).find("span").text.replace("-", "").replace("%", ""))
            print("Game inst price: "+tag.find("strike").text)  # game inst price
            temp_game.instance_price = int(tag.find("strike").text.replace(valute_symbol, "").replace(" ", ""))
            print("Game final price: "+tag.find("div", attrs={"class": "search_price"}).contents[3])  # game final price
            temp_game.final_price = int(tag.find("div", attrs={"class": "search_price"}).contents[3].replace(valute_symbol, "").replace(" ", ""))
        else:
            if tag.find("div", attrs={"class": "search_price"}).text.__len__() > 1 and "free" not in tag.find("div", attrs={"class": "search_price"}).text.lower():
                print("Game price: "+tag.find("div", attrs={"class": "search_price"}).text.strip())  # game final price
                temp_game.final_price = int(tag.find("div", attrs={"class": "search_price"}).text.strip().replace(valute_symbol, "").replace(" ", ""))
            else:
                print(f"Game price: 0{valute_simbol}")
                temp_game.final_price = 0
        print("Game image link: "+tag.find("img")["src"])
        temp_game.image_link = tag.find("img")["src"]
        temp_game.insert()
        break  # testing
    print("Game tags: ")
    print(game_tags)