import datetime

import requests
import json
from flask import Flask


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


def get_html():
    url = 'https://store.steampowered.com/'
    response = requests.get(url)
    data = response.text
    return data.replace("\r", "").replace("\t", "").replace("  ", "").replace("&nbsp;", "")


### Flask routes:


app = Flask(__name__)


@app.route("/")
def index():
    html = get_html()
    # html = get_div(cut_scripts(cut_head(html)), "", "\"tab_newreleases_content\"")
    html, head = cut_head(html)
    html = head \
           + "<body class=\"v6 infinite_scrolling responsive_page\">" \
           + get_elements_by_type(get_div(html, "", "\"tab_newreleases_content\""), "a", arg="data-ds-itemkey=\"App_") \
           + "</body>"
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
    clear_html = get_elements_by_type(get_div(clear_html, "", "\"tab_newreleases_content\""), "a", arg="data-ds-itemkey=\"App_")
    file = open("steam_new_releases_clear.html", "w", encoding="utf-8")
    file.write(clear_html)
    file.close()
    return clear_html


@app.route("/json")
def get_json():
    json_html = get_html()
    # html = get_div(cut_scripts(cut_head(html)), "", "\"tab_newreleases_content\"")
    json_html, head = cut_head(json_html)
    json_html = get_elements_by_type(get_div(json_html, "", "\"tab_newreleases_content\""), "a", arg="data-ds-itemkey=\"App_")
    new_json = "{scrap_date:"+datetime.datetime.now().__str__()+",games:["
    is_first = True
    for line in json_html.split("\n"):
        if "<a" in line and is_first:
            new_json += "{"
            is_first = False
        elif "<a" in line:
            new_json += ",{"
        elif "discount_pct" in line:
            new_json += "discount_percentage:"
            new_json += line.split(">")[1].split("<")[0] + ","
        elif "discount_original_price" in line:
            new_json += "discount_original_price:"
            new_json += line.split(">")[1].split("<")[0] + ","
        elif "discount_final_price" in line:
            new_json += "discount_final_price:"
            new_json += line.split(">")[1].split("<")[0] + ","
        elif "tab_item_name" in line:
            new_json += "game_name:"
            new_json += line.split(">")[1].split("<")[0]+","
        elif "tab_item_top_tags" in line:
            new_json += "tags:["
        elif "span" in line and "top_tag" in line:
            new_json += line.split(">")[1].split("<")[0].replace(", ", "") + ","
        elif "</a>" in line:
            new_json += "},"
    new_json += "]}"
    new_json = new_json.replace(",]", "]").replace(",}", "}").replace(":", " : ").replace(",\ntags : [}", "}")\
    .replace("}","\n}").replace("{", "{\n").replace(",", ",\n")
    #TODO доделать паринг - убрать пустые значения в json-е
    #TODO а лучше переделать принцип
    dumped_json = json.dumps(new_json, indent=5)
    file = open("steam_new_releases.json", "w", encoding="utf-8")
    file.write(dumped_json)
    file.close()
    return "<pre style=\"word-wrap: break-word; white-space: pre-wrap;\">"+new_json+"</pre>"


if __name__ == "__main__":
    app.run()
