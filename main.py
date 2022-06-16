import datetime
import flask
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import requests
import json
from flask import Flask
from os.path import isfile
import io
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from flask import Flask, render_template, request
import my_parser
import sql_controller

plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

### Flask routes:

app = Flask(__name__)


@app.route("/")
def index():
    # TODO оболочка сделана. Осталось сделать парсер более гибким и сделать взаимодействие с базой отдельно.
    # TODO а потом добавить рутов и их гет-пост обработку
    nav = open("templates/nav.html", encoding="utf-8").read()
    links = open("templates/links.html", encoding="utf-8").read()
    return render_template("Главная.html", nav=nav, links=links)


@app.route("/parser/", methods=['GET'])
def parser():
    nav = open("templates/nav.html", encoding="utf-8").read()
    links = open("templates/links.html", encoding="utf-8").read()
    return render_template("Парсер.html", nav=nav, links=links)


@app.route("/parser/", methods=['POST'])
def parser_post():
    nav = open("templates/nav.html", encoding="utf-8").read()
    links = open("templates/links.html", encoding="utf-8").read()

    print(request.form['genre'])
    parse_result = my_parser.parse(request.form['genre'])
    if parse_result == -1:
        return render_template("Парсер.html", nav=nav, links=links, error="Жанр не найден! Жанр должен начинаться с заглавной буквы и только на английском.")
    elif parse_result == -2:
        return render_template("Парсер.html", nav=nav, links=links, error="База данных не найдена. Проверьте целостность файла БД.")
    else:
        custom = sql_controller.TableController(file="steam_games.sqlite", t_name="games")
        custom.test_connect()
        qr = """
            SELECT 
            image_link, 
            games.name, 
            games.link, 
            final_price, 
            valute_symbol, 
            games.release_date,
            (select group_concat(game_tags.name) from game_tags where game_tags.id in (select game_to_game_tags.tag_id from game_to_game_tags where game_to_game_tags.game_id = games.id)) as tags
            from games
            """
        table_select = custom._custom_query_(qr)
        print(table_select)
        return render_template("Локальная-база-SQLite.html", nav=nav, links=links, table=table_select)


@app.route("/table/")
def table():
    nav = open("templates/nav.html", encoding="utf-8").read()
    links = open("templates/links.html", encoding="utf-8").read()

    custom = sql_controller.TableController(file="steam_games.sqlite", t_name="games")
    custom.test_connect()
    qr = """
    SELECT 
    image_link, 
    games.name, 
    games.link, 
    final_price, 
    valute_symbol, 
    games.release_date,
    (select group_concat(game_tags.name) from game_tags where game_tags.id in (select game_to_game_tags.tag_id from game_to_game_tags where game_to_game_tags.game_id = games.id)) as tags
    from games
    """
    table_select = custom._custom_query_(qr)
    if len(table_select):
        print("No data in Data Base")
        return render_template("Локальная-база-SQLite.html", nav=nav, links=links, table=table_select, error="No data in Data Base")
    print(len(table_select))
    return render_template("Локальная-база-SQLite.html", nav=nav, links=links, table=table_select)


if __name__ == "__main__":
    app.run(host="192.168.0.177", port="80")
