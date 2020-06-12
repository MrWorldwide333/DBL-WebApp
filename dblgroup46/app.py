from flask import Flask, render_template, url_for, request, jsonify
from bokeh.embed import server_document, components
from bokeh.layouts import column, row, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.tools import HoverTool
from bokeh.models.widgets import Select
from bokeh.plotting import figure
from bokeh.server.server import Server
from bokeh.themes import Theme
from tornado.ioloop import IOLoop
from bokeh.palettes import inferno
from bokeh.transform import factor_cmap

# from bokeh.embed import components

from bokeh.io import curdoc

import pymongo 
import pandas as pd
import numpy as np

app = Flask(__name__)




@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/vis")
def vis():
    return render_template('vis.html')

@app.route("/about")
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(threaded=True, port=5000)