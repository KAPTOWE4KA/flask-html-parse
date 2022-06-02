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

plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True


def cut_scripts(html):
    result = ""
    is_head = False
    for line in html.split("\n"):
        if "<script" in line:
            is_head = True
        if not is_head:
            result += line + "\n"
        if "</script>" in line:
            is_head = False
    return result


def cut_head(html):
    result = ""
    head = ""
    is_head = False
    for line in html.split("\n"):
        if "<head>" in line:
            is_head = True
        if not is_head:
            result += line + "\n"
        else:
            head += line + "\n"
        if "</head>" in line:
            is_head = False
    return result, head


def get_elements_by_type(html, ltype, arg=" "):
    result = ""
    is_element = False
    for line in html.split("\n"):
        if f"<{ltype}" in line and arg in line:
            is_element = True
        if is_element:
            result += line + "\n"
        if f"</{ltype}>" in line:
            is_element = False
    return result


def get_div(html, div_class="", div_id=""):
    # returns first div with class and id
    result = ""
    search_word = ""
    if div_id == "":
        if div_class == "":
            search_word = " "
        else:
            search_word = div_class
    else:
        search_word = div_id
    is_needed_div = False
    close_bkt_count = 1
    for line in html.split("\n"):
        if is_needed_div:
            result += line + "\n"
        if "<div" in line and search_word in line:
            is_needed_div = True
        elif "<div" in line:
            close_bkt_count += 1
        elif "</div>" in line:
            close_bkt_count -= 1
        if close_bkt_count == 0:
            is_needed_div = False
    return result


def int_from_price(price_str):
    number = ""
    for char in price_str:
        if char in "0123456789":
            number += char
    return int(number)


def get_html():
    url = 'https://store.steampowered.com/'
    response = requests.get(url)
    data = response.text
    return data.replace("\r", "").replace("\t", "").replace("  ", "").replace("&nbsp;", "")


def discount_average():
    if not isfile("steam_new_releases.json"):
        get_json()
    file = open("steam_new_releases.json", "r", encoding="utf-8")
    data_json = json.loads(file.read())
    size = 0
    discounts = 0
    for game in data_json['games']:
        try:
            discounts += game['discount_percentage']
            size += 1
        except KeyError as e:
            print(f"{game['game_name']} не имеет скидку")
    return round(discounts / size, 2)


def price_average():
    if not isfile("steam_new_releases.json"):
        get_json()
    file = open("steam_new_releases.json", "r", encoding="utf-8")
    data_json = json.loads(file.read())
    size = len(data_json['games'])
    prices = 0
    for game in data_json['games']:
        try:
            if game['final_price'] != 0:
                prices += game['final_price']
        except KeyError as e:
            print(f"{game['game_name']} не имеет показатель цены")
    return round(prices / size, 2)


def free_percentage():
    if not isfile("steam_new_releases.json"):
        get_json()
    file = open("steam_new_releases.json", "r", encoding="utf-8")
    data_json = json.loads(file.read())
    size = 0
    free_count = 0
    for game in data_json['games']:
        try:
            size += 1
            if game['final_price'] == 0:
                free_count += 1
        except KeyError as e:
            print(f"{game['game_name']} не имеет показатель цены")
    return round(free_count / size*100, 2)


### Flask routes:


app = Flask(__name__)


@app.route("/")
def index():
    html = get_html()
    # html = get_div(cut_scripts(cut_head(html)), "", "\"tab_newreleases_content\"")
    html, head = cut_head(html)
    html = """
        <h3>Меню</h3>
        <a href="/json">Получить список игр в тренде Steam в виде JSON</a><br><br>
        <a href="/analytics">Неполная аналитика по играм в тренде на главной странице Steam</a>
        """
    # для красоты оставил класс на body и голову страницы
    file = open("steam_new_releases.html", "w", encoding="utf-8")
    file.write(html)
    file.close()
    return html


@app.route("/clear")
def clear():
    clear_html = get_html()
    # html = get_div(cut_scripts(cut_head(html)), "", "\"tab_newreleases_content\"")
    clear_html, head = cut_head(clear_html)
    clear_html = get_elements_by_type(get_div(clear_html, "", "\"tab_newreleases_content\""), "a",
                                      arg="data-ds-itemkey=\"App_")
    file = open("steam_new_releases_clear.html", "w", encoding="utf-8")
    file.write(clear_html)
    file.close()
    return clear_html


@app.route("/json")
def get_json():
    json_html = get_html()
    # html = get_div(cut_scripts(cut_head(html)), "", "\"tab_newreleases_content\"")
    json_html, head = cut_head(json_html)
    json_html = get_elements_by_type(get_div(json_html, "", "\"tab_newreleases_content\""), "a",
                                     arg="data-ds-itemkey=\"App_")
    new_json = dict()
    new_json['games'] = []
    a_blocks = json_html.split("</a>")
    # print(a_blocks[1])
    no_duplicates = []
    for block in a_blocks:
        if "</body>" in block or block == "\n":
            break
        if block.split("tab_item_name\">")[1].split("</div")[0] not in no_duplicates:
            new_json['games'].append({})
            for line in block.split("\n"):
                if line == "\n" or line == "":
                    continue
                if "tab_item_top_tags" in line:
                    tags = line.split("tab_item_top_tags\">")[1].split("</div>")[0].replace("<span class=\"top_tag\">",
                                                                                            "").replace("</span>",
                                                                                                        "").split(", ")
                    # print(tags)
                    new_json['games'][-1]['tags'] = tags
                if "tab_item_name" in line:
                    # print("LINE: \""+line+"\"")
                    # print("GAME_NAME: \""+line.split(">")[1].split("<")[0]+"\"")
                    new_json['games'][-1]['game_name'] = line.split(">")[1].split("<")[0]
                    no_duplicates.append(line.split(">")[1].split("<")[0])
                if "discount_pct" in line:
                    # print("DISCOUNT: \"" + line.split("discount_pct\">")[1].split("<")[0] + "\"")
                    new_json['games'][-1]['discount_percentage'] = int_from_price(
                        line.split("discount_pct\">")[1].split("<")[0])
                if "discount_original_price" in line:
                    # print("ORIGINAL_PRICE: \"" + int_from_price(line.split("discount_original_price\">")[1].split("<")[0]) + "\"")
                    new_json['games'][-1]['original_price'] = int_from_price(
                        line.split("discount_original_price\">")[1].split("<")[0])
                if "discount_final_price" in line:
                    # print("FINAL_PRICE: \"" + int_from_price(line.split("discount_final_price\">")[1].split("<")[0]) + "\"")
                    if "Free" not in line:
                        new_json['games'][-1]['final_price'] = int_from_price(
                            line.split("discount_final_price\">")[1].split("<")[0])
                    else:
                        new_json['games'][-1]['final_price'] = 0
                        # Free to play or Free
    dumped_json = json.dumps(new_json, indent=5).encode("utf-8")
    file = open("steam_new_releases.json", "w", encoding="utf-8")
    file.write(dumped_json.decode("utf-8"))
    file.close()
    return "<pre style=\"word-wrap: break-word; white-space: pre-wrap;\">" + dumped_json.decode("utf-8") + "</pre>"


@app.route("/analytics")
def get_plot():
    return f"""
            <h2>График популярности тегов (на главной странице / не все)</h2><img src="/plot.png" alt="Plot not found">
            <h3>Доля бесплатных игр в трендах (на главной странице): {free_percentage()}%</h2>
            <h3> Средняя цена игр в трендах (на главной странице): {price_average()} </h2>
            <h3> Средняя скидка (без учета игр без скидок) игр в трендах (на главной странице): {discount_average()}%</h2>
            <a href="/json">Получить список игр в тренде Steam в виде JSON</a><br><br>
            <a href="/">Наза в меню</a><br><br>
           """


@app.route("/plot.png")
def get_plot_tags():
    if not isfile("steam_new_releases.json"):
        get_json()
    file = open("steam_new_releases.json", "r", encoding="utf-8")
    data_json = json.loads(file.read())
    tags = {}
    for game in data_json['games']:
        if len(game["tags"]) > 0:
            for tag in game["tags"]:
                if tag not in tags.keys():
                    tags[tag] = 1
                else:
                    tags[tag] += 1
    fig = Figure(figsize=[14, 7], dpi=100)
    axis = fig.add_subplot(1, 1, 1)
    no_solo_tags = {}
    for key in tags.keys():
        if tags[key] > 6:
            #print(tags[key])
            no_solo_tags[key] = tags[key]
    xs = [t for t in no_solo_tags.keys()]  # np.random.rand(100)
    #print(xs)
    ys = [t for t in no_solo_tags.values()]  # np.random.rand(100)
    #print(ys)
    # axis.hist(no_solo_tags, orientation='horizontal')#orientation='horizontal'
    axis.bar(xs, ys, width=0.7)  # orientation='horizontal'
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


if __name__ == "__main__":
    app.run()
