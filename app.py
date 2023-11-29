#!/usr/bin/env python
# coding: utf-8

# In[52]:


import requests
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import numpy as np
import json

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go
from plotly.colors import DEFAULT_PLOTLY_COLORS


# In[53]:


url = 'http://openAPI.seoul.go.kr:8088/4f744d4b496172693432706e71704b/json/MonthlyAverageAirQuality/1/50/202303'

r = requests.get(url)
data = r.json()
data

df = pd.DataFrame(data['MonthlyAverageAirQuality']['row'])

df['MSRSTE_NM'] = df['MSRSTE_NM'].astype(str)

MSRSTE_name = ['강동구','송파구','강남구','서초구','동작구','관악구','금천구','영등포구','구로구','양천구','강서구','광진구','중랑구','노원구','동대문구','성동구','도봉구','성북구','강북구','종로구','중구','용산구','서대문구','마포구','은평구']

gu = df[df['MSRSTE_NM'].isin(MSRSTE_name)]

air = gu.reset_index(drop=True)

url = 'https://sgisapi.kostat.go.kr/OpenAPI3/auth/authentication.json'
param = {'consumer_key':'d08621e7a06b4dfcb84b',
         'consumer_secret':'cbd9ff8be5204353a24e'}

r = requests.get(url = url, params = param)
r

data = r.json()
data

token = data['result']['accessToken']

geourl = 'https://sgisapi.kostat.go.kr/OpenAPI3/boundary/hadmarea.geojson'
geoparam = {'accessToken' : token, 
            'year' : 2022, 
            'adm_cd' : '11', 
            'low_search' : 1}

geos = requests.get(geourl, geoparam)

data = geos.json()

s_emd = gpd.GeoDataFrame.from_features(data['features'])

s_emd['adm_nm'] = s_emd['adm_nm'].str.replace('서울특별시', '')

s_emd = s_emd.sort_values(by = 'adm_nm', ascending = True)
s_emd = s_emd.reset_index(drop=False)

data = pd.concat([air,s_emd],axis=1)
data = data.drop('adm_nm',axis=1)

geom = gpd.points_from_xy(data['x'],data['y'], crs = 'epsg:5179')
seoul = gpd.GeoDataFrame(data, geometry = data['geometry'])

seoul = seoul.set_crs(5179)

sheldt = pd.read_table('c:/analysis/미세먼지대피소.csv', header = 0, sep = ',',encoding = 'utf-8')

geom = gpd.points_from_xy(sheldt['Longitude'] ,sheldt['Latitude'], crs = 4326)
shelter = gpd.GeoDataFrame(sheldt, geometry = geom)
shelter = shelter.to_crs(5179)

gdf = gpd.read_file('c:/analysis/seoul_emd.shp')
gdf = gdf.to_crs(5179)


# In[54]:


gu = list(data['MSRSTE_NM'])
gu.sort()


# In[55]:


shelter['구'] = shelter['대피소 상세주소'].str.extract('(\S+)[구]')
shelter['구'] = shelter['구'] + '구'


# In[56]:


fig, ax = plt.subplots(figsize=(7, 7))
shelter.plot(ax = ax, color = 'green', markersize = 7)
gdf.boundary.plot(ax = ax, color = 'black', linewidth = 0.1)

plt.rcParams['axes.unicode_minus'] = False
plt.title('서울시 미세먼지 대피소 위치 현황')
plt.rcParams["font.family"] = 'NanumGothic'


# In[67]:


seoul_shel = shelter[['대피소 명칭', '대피소 상세주소', '최대수용가능인원', 'Latitude', 'Longitude','구']]

shel_gu = list(seoul_shel['구'])
shel_gu.sort()
seoul_shel.query('구 == "강남구"')


# In[58]:


seoul = seoul.to_crs(4326)
seoul_json = seoul.__geo_interface__


# In[59]:


from dash import Dash, dcc, html, Input, Output, State

# app structure
app = Dash(__name__)
app.title = ('Dashboard | Seoul Shelter Data')
server = app.server

# App layout
app.layout = html.Div([
    html.H1('Seoul Shelter Data',
            style = {'textAlign': 'center', 
                     'marginBottom': 10, 
                     'marginTop': 10}),
    dcc.Tabs([
        dcc.Tab(label = 'Fine dust Shelter',
                children =[
                    html.Div([
                    
                        html.Div(className = 'PM',
                                 children = [html.Div(dcc.Dropdown(id = 'id_gu',
                                                                   options = [{'label': i, 'value': i} for i in gu],
                                                                   value = max(gu),
                                                                   style = {'width': '45%'})),
                                             html.Div(dcc.Graph(id = 'map'))
                                             ])
                            ], style = {'float': 'left', 'display': 'inline-block', 'width': '55%'}),
                        html.Div([
                            html.Div(className = 'shelt',
                                    children = [html.Div(dcc.Graph(id = 'shelter'))]
                                    )
                                ], style = {'float': 'right', 'width': '45%'})
                              ]
               ),
        dcc.Tab(label = 'Earthquake shelter'),
        dcc.Tab(label = 'Inundation shelter'),
        dcc.Tab(label = 'Cooling centre')
            ])
        ])


# In[60]:


@app.callback(Output('map', 'figure'),
              Input('id_gu', 'value'))

def update_output(val):
    
    # data
    df_map = seoul[seoul['MSRSTE_NM'] == val]
    df_map = df_map.loc[:, ['MSRSTE_NM', 'PM10']]

    # hover_text
    df_map['text'] = df_map['MSRSTE_NM'] + \
                     df_map['PM10'].astype(str) + 'µg/m³'
    
    trace = go.Choropleth(geojson = seoul_json,
                          locations = df_map.index,
                          z = df_map['PM10'],
                          text = df_map['text'],
                          hoverinfo = 'text',
                          colorscale = 'Viridis',
                          autocolorscale = False,
                          reversescale = False,
                          marker_line_color = 'darkgray',
                          marker_line_width = 0.5,
                          
                          # colorbar option = legend bar
                          colorbar_title = 'PM10 (µg/m³)',
                          colorbar_thickness = 15,
                          colorbar_len = 1,
                          colorbar_x = 1.01,
                          colorbar_ticklen = 10
                         )
    
    layout = go.Layout(title = 'Seoul PM10 Map',
                       geo = dict(showframe = True,
                                  showcoastlines = False,
                                  projection_type = 'equirectangular'),
                       height = 420, margin = dict(l=50, r=50, b=20, t=50))
    
    figure = go.Figure(trace, layout)
    return figure


# In[64]:


@app.callback(Output('shelter','figure'),
             Input('id_gu','value'))

def update_output(val):
    
    place = seoul_shel.loc[seoul_shel['구'] == val]
    place = place.loc[:, ['대피소 명칭', '대피소 상세주소', '최대수용가능인원', 'Latitude', 'Longitude', '구']]
    
    place['text'] = place['대피소 상세주소'] + ' ' + '|' + ' ' + \
                    place['최대수용가능인원'].astype(str) + '명'
    
    trace = go.Scattergeo(lat = place['Latitude'], lon = place['Longitude'],
                          mode = 'markers',
                          marker = dict(symbol = 'circle',
                                        size = np.sqrt(place['최대수용가능인원'])),
                          text = place['text'],
                          hoverinfo = 'text')
    
    dat = [trace]
    
    layout = go.Layout(title = 'Shelter Map',
                       geo = dict(scope = 'asia',
                                  projection_type = 'equirectangular',
                                  showcountries = True))
    
    figure = go.Figure(dat, layout)
    
    return figure


# In[62]:


if __name__=='__main__':
    app.run_server(debug = False)
