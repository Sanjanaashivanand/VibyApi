#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 11:46:09 2022

@author: sanjanashivanand
"""

import numpy as np
import pandas as pd
import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import sys
from datetime import timedelta

CLIENT_ID = "025b3fc46b48490c9d2b54cbf1d12888"
CLIENT_SECRET = "c0344ada6e0c4f67b480c0e9c08f1975"

sp = None

class SpotifyFunctions:
    
    def __init__(self):
        
        self.CLIENT_ID = "025b3fc46b48490c9d2b54cbf1d12888"
        self.CLIENT_SECRET = "c0344ada6e0c4f67b480c0e9c08f1975"
        self.sp = self.Auth()
    
    def Auth(self):
        client_credentials_manager = SpotifyClientCredentials(client_id=self.CLIENT_ID, client_secret=self.CLIENT_SECRET)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        return sp
    
    def getUsersPlaylists(self, username='Spotify'):  
        playlistNames = []
        playlistUris = []
        playlists = self.sp.user_playlists(username)

        for p in playlists['items']:
            playlistNames.append(p['name'].encode('ascii', 'ignore').decode('ascii'))
            playlistUris.append(p['uri'].split(':')[2])
        
        return pd.DataFrame({'name' : playlistNames, 'uri' : playlistUris}, \
        columns=['name', 'uri'])
    
    def getName(self,tracks):
        tl = []

        for i, item in enumerate(tracks['items']):
            track = item['track']
            song_id = track['id']
            track_name = track['name']

            if len(track['artists'])>1:
                mul_artists = []
                for artist in track['artists']:
                    mul_artists.append(artist['name'])
                artist_name = mul_artists
            else:
                artist_name = track['artists'][0]['name']

            album_name = track['album']['name']

            if len(track['album']['images'])==0:
                album_cover = "-999"
            else:
                album_cover = track['album']['images'][0]

            release_date = track['album']['release_date']
            preview_link  = track['preview_url']
            spotify_link = track['external_urls']['spotify']
            tl.append((song_id, track_name, artist_name, album_name, album_cover, release_date, preview_link,spotify_link))
        
        return tl

    def getSongsFromPlaylist(self,uri,username):
        trackList = []
        results = self.sp.user_playlist(username,uri)
        tracks = results['tracks']
        
        trackList.extend(self.getName(tracks))
        
        while(tracks['next']):
                tracks = self.sp.next(tracks)
                trackList.extend(self.getName(tracks))
        
        song_id = [tuple[0] for tuple in trackList]
        track_name = [tuple[1] for tuple in trackList]
        artist_name = [tuple[2] for tuple in trackList]
        album_name = [tuple[3] for tuple in trackList]
        album_cover = [tuple[4] for tuple in trackList]
        release_date = [tuple[5] for tuple in trackList]
        preview_link = [tuple[6] for tuple in trackList]
        spotify_link = [tuple[7] for tuple in trackList]
        return pd.DataFrame(data={'id': song_id, 'track_name': track_name, 'artist_name': artist_name, 
                                'album_name': album_name,'album_cover': album_cover, 'release_date': release_date, 
                                'preview_link':preview_link,'spotify_link':spotify_link})

    def getFeatures(self,songsDF):
        
        id = []
        names = []
        acousticness = []
        danceability = []
        energy = []
        instrumentalness = []
        liveness = []
        loudness = []
        speechiness = []
        tempo = []
        valence = []
        timeSignature = []
        length = []

        for index, row in songsDF.iterrows():
                uri = row['id']
                if(not isinstance(uri, str)):
                    continue
                name = row['track_name']
                features =self.sp.audio_features(uri)
                if features != [None]:
                    id.append(uri)
                    names.append(name)
                    length.append(
                        timedelta(milliseconds=features[0]['duration_ms']))
                    acousticness.append(features[0]['acousticness'])
                    danceability.append(features[0]['danceability'])
                    energy.append(features[0]['energy'])
                    instrumentalness.append(features[0]['instrumentalness'])
                    liveness.append(features[0]['liveness'])
                    loudness.append(features[0]['loudness'])
                    speechiness.append(features[0]['speechiness'])
                    tempo.append(features[0]['tempo'])
                    valence.append(features[0]['valence'])
                    timeSignature.append(features[0]['time_signature'])

        data = {
            'id': id,
            'name': names,
            'length': length,
            'acousticness': acousticness,
            'danceability': danceability,
            'energy': energy,
            'instrumentalness': instrumentalness,
            'liveness': liveness,
            'loudness': loudness,
            'speechiness': speechiness,
            'tempo': tempo,
            'valence': valence,
            'timeSignature': timeSignature
        }

        return pd.DataFrame(data)
    
        