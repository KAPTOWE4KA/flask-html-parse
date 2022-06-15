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
        return render_template("Локальная-база-SQLite.html", nav=nav, links=links)


@app.route("/table/")
def table():
    nav = open("templates/nav.html", encoding="utf-8").read()
    links = open("templates/links.html", encoding="utf-8").read()
    return render_template("Локальная-база-SQLite.html", nav=nav, links=links)


if __name__ == "__main__":
    app.run()
