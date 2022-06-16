"""
Created on Sun May 15 02:24:49 2022
@author: sanjanashivanand
"""

from crypt import methods
import flask 
from flask import request,jsonify, Response
import pandas as pd
import numpy as np
import tekore as tk
from flask_cors import CORS
import math

df = pd.read_csv('Dataset.csv').fillna("null")
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

def RecommendationsbyMood(val,ref_df,n_recs=5):
    ref_df['distances'] = ref_df['valence'].apply(lambda x: math.sqrt((x-val)**2))
    
    if val<=0.6:
        ref_df_sorted = ref_df.sort_values(by = "distances", ascending=False)
    else:
        ref_df_sorted = ref_df.sort_values(by = "distances", ascending=True)
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

def getSongs(sample):
    recs = df.sample(n=sample).to_dict()
    songs = []
    song_id = []
    for i in recs['id'].keys():
        song_id.append(i)
    
    for n in song_id:
        song_details = {}
        for j in recs.keys():
            song_details[j] = recs[j][n]
        songs.append(song_details)
    return songs


app = flask.Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    
    id = request.args['id']
    n_recs = int(request.args.get('n_recs', 5))
    try:
        spotify = authorize()
        print(n_recs)
        return jsonify(getRecommendations(track_id=id, ref_df=df, sp=spotify, n_recs=n_recs))
    except:
        return "Invalid ID"

@app.route('/dashboard', methods=['GET'])
def dashboard():
    n = int(request.args.get('n',100))
    
    try:
        return jsonify(getSongs(n))
    except:
        return "An Error has occured"

@app.route('/getSongsbyMood', methods=['GET'])
def getSongsbyMood():
    val = float(request.args['val'])
    n_recs = int(request.args.get('n_recs',5))

    try:
        return jsonify(RecommendationsbyMood(val=val, ref_df=df, n_recs=n_recs))
    except: 
        return "An error has occured"    

@app.route('/Playlist/Model1', methods=['GET'])
def getSongsFromM1():
    mood = request.args['mood'].capitalize()
    print("MOOD",mood)
    try:
        playlist = pd.read_csv('./Models/M1Playlists/' + mood + '.csv').fillna("null")
        return Response(playlist.to_json(orient="records"), mimetype='application/json')
    except:
        return "<h1>No playlist found</h1>"

@app.route('/Playlist/Model2', methods=['GET'])
def getSongsFromM2():
    mood = request.args['mood'].capitalize()
    print("MOOD",mood)
    try:
        playlist = pd.read_csv('./Models/M2Playlists/' + mood + '.csv').fillna("null")
        return Response(playlist.to_json(orient="records"), mimetype='application/json')
    except:
        return "<h1>No playlist found</h1>"