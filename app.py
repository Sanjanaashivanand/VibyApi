#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 15 02:24:49 2022

@author: sanjanashivanand
"""

import flask 
from flask import request
import pandas as pd
import numpy as np
import tekore as tk
import json

df = pd.read_csv('Dataset.csv')
df["[val,energy]"] = df[["valence", "energy"]].values.tolist()

def distance(p1, p2):
    dis_x = p2[0] - p1[0]
    dis_y = p2[1] - p1[1]
    dis = (dis_x ** 2 + dis_y ** 2) ** (1/2)
    return dis

def authorize():
    CLIENT_ID = "025b3fc46b48490c9d2b54cbf1d12888"
    CLIENT_SECRET = "c0344ada6e0c4f67b480c0e9c08f1975"
    app_token = tk.request_client_token(CLIENT_ID, CLIENT_SECRET)
    return tk.Spotify(app_token)

spotify = authorize()

def getRecommendations(track_id, ref_df, sp, n_recs = 5):
    track_features = sp.track_audio_features(track_id)
    track_moodvec = np.array([track_features.valence, track_features.energy])

    ref_df["distances"] = ref_df["[val,energy]"].apply(lambda x: distance(track_moodvec,np.array(x)))
    ref_df_sorted = ref_df.sort_values(by = "distances", ascending = True)
    ref_df_sorted = ref_df_sorted[ref_df_sorted["id"] != track_id]
    recs = ref_df_sorted.iloc[:n_recs]
    recommendations = []
    song_id = []
    for i in recs['id'].keys():
        song_id.append(i)
    
    for n in song_id:
        song_details = {}
        for j in recs.keys():
            song_details[j] = recs[j][n]
        recommendations.append(song_details)
    
    return recommendations

app = flask.Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    
    id = request.args['id']
 
    
    try:
        return getRecommendations(track_id = id, ref_df = df, sp = spotify, n_recs = 5)
    except KeyError:
        return "Not in the Database"