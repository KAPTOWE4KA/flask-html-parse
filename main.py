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

plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

### Flask routes:

app = Flask(__name__)


@app.route("/")
def index():
    # TODO оболочка сделана. Осталось сделать парсер более гибким и сделать взаимодействие с базой отдельно.
    # TODO а потом добавить рутов и их гет-пост обработку
    #nav = open("templates/nav.html", encoding="utf-8").read()
    return render_template("index.html")#, nav=nav)



if __name__ == "__main__":
    app.run()
