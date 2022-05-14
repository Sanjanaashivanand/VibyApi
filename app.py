#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 15 02:24:49 2022

@author: sanjanashivanand
"""

import flask 
from flask import request
import pandas as pd

df = pd.read_csv('Dataset.csv')

app = flask.Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    id = request.args['id']
    try:
        return id
    except KeyError:
        return "Not in the Database"