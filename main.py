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
import telebot
from telebot import types
from telebot import apihelper
import os
import time
import config

TOKEN = config.telegram_bot_token

plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

# apihelper.proxy = {
# 'http': 'http://23.227.38.122:80',
# 'http': 'http://23.227.38.122:80'
# }


bot = telebot.TeleBot(TOKEN)

print("Telebot started")


# filter applied to groups or channels (NO PRIVATE CHATS)
class IsAdmin(telebot.custom_filters.SimpleCustomFilter):
    # Class will check whether the user is admin or creator in group or not
    key = 'is_admin'

    @staticmethod
    def check(message: telebot.types.Message):
        print(bot.get_chat_member(message.chat.id, message.from_user.id).status)
        print(message.chat.type)
        return bot.get_chat_member(message.chat.id, message.from_user.id).status in ['administrator',
                                                                                     'creator'] and message.chat.type in [
                   'group', 'channel']


# To register filter, you need to use method add_custom_filter.
bot.add_custom_filter(IsAdmin())


# Команды
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Ссылка на github",
                                         url='https://github.com/KAPTOWE4KA/flask-html-parse/tree/telegram-bot-add')
    markup.add(button1)
    bot.send_message(message.chat.id,
                     f"Привет {message.from_user.first_name}! Это тестовый бот телеграмм. Нажми на кнопку, чтобы перейти на github этого бота. Напиши команду /menu для перехода в меню комманд бота.",
                     reply_markup=markup)


@bot.message_handler(commands=['analytics'])
def get_analytics(message):
    bot.send_message(message.chat.id, f"""Доля бесплатных игр в трендах (на главной странице): {free_percentage()}%
        Средняя цена игр в трендах (на главной странице): {price_average()} 
        Средняя скидка (без учета игр без скидок) игр в трендах (на главной странице): {discount_average()}% """)


@bot.message_handler(commands=['get_html'])
def get_html_tele(message):
    if message.text.split(" ").__len__() > 1:
        if message.text.split(" ")[1] == "help":
            bot.send_message(chat_id=message.chat.id, text="Доступные аргументы для команды /get_html: help, new")
        elif message.text.split(" ")[1] == "new":
            clear_html = get_html()
            # html = get_div(cut_scripts(cut_head(html)), "", "\"tab_newreleases_content\"")
            clear_html, head = cut_head(clear_html)
            clear_html = get_elements_by_type(get_div(clear_html, "", "\"tab_newreleases_content\""), "a",
                                              arg="data-ds-itemkey=\"App_")
            file = open("steam_new_releases_clear.html", "w", encoding="utf-8")
            file.write(clear_html)
            file.close()
            with open("steam_new_releases_clear.html", 'r', encoding="utf-8") as data:
                bot.send_document(chat_id=message.chat.id, document=data)
    else:
        bot.send_message(chat_id=message.chat.id,
                         text="Отсутствуют нужные аргументы у команды. Для помощи напишите /get_html help")


@bot.message_handler(commands=['menu'])
def menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/start")
    btn2 = types.KeyboardButton("/menu")
    btn4 = types.KeyboardButton("/plot")
    btn5 = types.KeyboardButton("/json")
    btn6 = types.KeyboardButton("/get_html help")
    btn7 = types.KeyboardButton("/analytics")
    markup.add(btn1, btn2, btn4, btn5, btn6, btn7)
    bot.send_message(message.chat.id,
                     text=f"Привет, {message.from_user.first_name}! Меню команд появится у тебя под строкой сообщений.",
                     reply_markup=markup)


@bot.message_handler(commands=['json'])
def plot_tele(message):
    if not isfile("steam_new_releases.json"):
        get_json()
    with open("steam_new_releases.json", "r", encoding="utf-8") as data:
        bot.send_document(message.chat.id, document=data)


@bot.message_handler(commands=['plot'])
def plot_tele(message):
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
            # print(tags[key])
            no_solo_tags[key] = tags[key]
    xs = [t for t in no_solo_tags.keys()]  # np.random.rand(100)
    # print(xs)
    ys = [t for t in no_solo_tags.values()]  # np.random.rand(100)
    # print(ys)
    # axis.hist(no_solo_tags, orientation='horizontal')#orientation='horizontal'
    axis.bar(xs, ys, width=0.7)  # orientation='horizontal'
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    bot.send_photo(chat_id=message.chat.id, photo=output.getvalue())
    # return Response(output.getvalue(), mimetype='image/png')


@bot.message_handler(commands=['timer'], is_admin=True)
def timer(message):
    for i in range(5):
        time.sleep(1)
        bot.send_message(chat_id=message.chat.id, text=str(i + 1))


# Остальной текст
@bot.message_handler(content_types=['text'])
def menu_check(message):
    bot.send_message(message.chat.id, text="Вы что-то написали боту, но он пока не знает что вам на это ответить...")


# Pictures
@bot.message_handler(content_types=["sticker"])
def send_sticker(message):
    print(message)
    bot.send_message(message.chat.id, 'No stickers please')
    bot.delete_message(chat_id=message.chat.id, message_id=message.id)


# html parse block


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
    return round(free_count / size * 100, 2)


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


bot.polling()
