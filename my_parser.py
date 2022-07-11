import os

from bs4 import BeautifulSoup
import requests as req
from sql_controller import TableController
from class_game import Game
from class_game import Games, Game_Tags, Base, engine
from sqlalchemy.orm import sessionmaker


def parse(genre=""):
    url = "https://store.steampowered.com/search/results?sort_by=Released_DESC&force_infinite=1"
    if genre != "":
        url += f"&genre={genre}"
    resp = req.get(url)
    #print(f"URL: {url}")
    soup = BeautifulSoup(resp.text, "lxml")
    results = soup.find("div", id="search_resultsRows")
    # pages = soup.find("div", id="search_pagination_right").find_all("a")
    # max_pages = 1
    # for a in pages:
    #     max()
    result_count = int(
        soup.find("div", id="search_results_filtered_warning").find_next("div").text.split(" ")[0].replace(",", ""))
    #print(result_count)
    if result_count > 100000:  # if games more than 100000 then genre is not exist
        return -1
    # Старый подход:
    # games_table = TableController("steam_games.sqlite", "games")
    # tags_table = TableController("steam_games.sqlite", "game_tags")
    # game_2_tag_table = TableController("steam_games.sqlite", "game_to_game_tags")

    # Новый подход через SQLAlchemy
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    valute_symbol = ""
    for tag in results.find_all("a"):  # searching valute simbol to use it further
        if tag.find("div", attrs={"class": "search_price"}).text.__len__() > 2 and "free" not in tag.find("div", attrs={"class": "search_price"}).text.lower():
            valute_symbol = tag.find("div", attrs={"class": "search_price"}).text.strip()[-1]
            break

    for tag in results.find_all("a"):
        #print("Game link: " + tag['href'])
        link = tag['href']
        tags_soup = BeautifulSoup(req.get(tag['href']).text, "lxml").find_all("a", attrs={"class": "app_tag"})
        #print("Game id: " + tag['data-ds-itemkey'])  # game id
        gid = int(tag['data-ds-itemkey'].replace("App_", ""))
        if session.query(Games).filter_by(id=gid).first():
            continue
        #print("Game name: " + tag.find("span", attrs={"class": "title"}).text)  # game name
        name = tag.find("span", attrs={"class": "title"}).text.replace("'", "''")
        #print("Game release date: " + tag.find("div", attrs={"class": "search_released"}).text)  # release date
        release_date = tag.find("div", attrs={"class": "search_released"}).text
        if tag.find("strike"):
            #print("Game discount: " + tag.find("div", attrs={"class": "search_discount"}).find("span").text)  # discount
            discount = int(
                tag.find("div", attrs={"class": "search_discount"}).find("span").text.replace("-", "").replace("%", ""))
            #print("Game inst price: " + tag.find("strike").text)  # game inst price
            instance_price = int(tag.find("strike").text.replace(valute_symbol, "").replace(" ", ""))
            #print("Game final price: " + tag.find("div", attrs={"class": "search_price"}).contents[3])  # game final price
            final_price = int(
                tag.find("div", attrs={"class": "search_price"}).contents[3].replace(valute_symbol, "").replace(" ", ""))
        else:
            discount = 0
            if tag.find("div", attrs={"class": "search_price"}).text.__len__() > 1 and "free" not in tag.find("div",attrs={"class": "search_price"}).text.lower():
                #print(
                #     "Game price: " + tag.find("div", attrs={"class": "search_price"}).text.strip())  # game final price
                final_price = int(tag.find("div", attrs={"class": "search_price"}).text.strip().replace(valute_symbol, "").replace(" ", ""))
            else:
                #print(f"Game price: 0{valute_symbol}")
                final_price = 0
        #print("Game image link: " + tag.find("img")["src"])
        image_link = tag.find("img")["src"]
        if discount==0:
            temp_game = Games(gid, name, release_date, final_price, link, image_link, valute_symbol)
        else:
            temp_game = Games(gid, name, release_date, final_price,link,image_link,valute_symbol, discount=discount, instance_price=instance_price)
        for game_tag in tags_soup:
            if not session.query(Game_Tags).filter_by(name=game_tag.text.strip().replace("'", "''")).first():
                ttag = Game_Tags(game_tag.text.strip().replace("'", "''"))
                temp_game.tags.append(ttag)
            else:
                temp_game.tags.append(session.query(Game_Tags).filter_by(name=game_tag.text.strip().replace("'", "''")).first())

        if not session.query(Games).filter_by(name=temp_game.name).first():
            session.add(temp_game)
        session.commit()
        session.close()

    #print("Game tags: ")
    #print(game_tags)
