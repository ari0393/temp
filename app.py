#!/usr/bin/env python
# coding: utf-8

# In[199]:


import requests

import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import numpy as np
import json
import folium

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go
from plotly.colors import DEFAULT_PLOTLY_COLORS
import plotly.express as px


# In[200]:


#김아리

url = 'http://openAPI.seoul.go.kr:8088/4f744d4b496172693432706e71704b/json/MonthlyAverageAirQuality/1/50/202303'

r = requests.get(url)
data = r.json()
data

dfs = pd.DataFrame(data['MonthlyAverageAirQuality']['row'])

dfs['MSRSTE_NM'] = dfs['MSRSTE_NM'].astype(str)

MSRSTE_name = ['강동구','송파구','강남구','서초구','동작구','관악구','금천구','영등포구','구로구','양천구','강서구','광진구','중랑구','노원구','동대문구','성동구','도봉구','성북구','강북구','종로구','중구','용산구','서대문구','마포구','은평구']

gu = dfs[dfs['MSRSTE_NM'].isin(MSRSTE_name)]

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

gu = list(data['MSRSTE_NM'])
gu.sort()

shelter['구'] = shelter['대피소 상세주소'].str.extract('(\S+)[구]')
shelter['구'] = shelter['구'] + '구'

seoul_shel = shelter[['대피소 명칭', '대피소 상세주소', '최대수용가능인원', 'Latitude', 'Longitude','구']]

shel_gu = list(seoul_shel['구'])
shel_gu.sort()

seoul = seoul.to_crs(4326)
seoul_json = seoul.__geo_interface__

shelters = shelter.to_crs(4326)
shelter_json = shelters.__geo_interface__


# In[201]:


#이윤진

url= 'https://sgisapi.kostat.go.kr/OpenAPI3/auth/authentication.json?consumer_key=47e9c3502a8a4bf09b4d&consumer_secret=9bd5928286144a2cbcd2'
r=requests.get(url=url)

datas=r.json()
datas

token=datas['result']['accessToken']
token

url='https://sgisapi.kostat.go.kr/OpenAPI3/boundary/hadmarea.geojson'
parameter = {'accessToken':token, 'year':2022, 'adm_cd':11, 'low_search':1}

r= requests.get(url=url,params=parameter)
a_emd = r.json()

s_emds = gpd.GeoDataFrame.from_features(a_emd['features'])

s_emds['adm_nm'] = s_emds['adm_nm'].str.replace('서울특별시', '')

s_emds = s_emds.sort_values(by = 'adm_nm', ascending = True)
s_emds = s_emds.reset_index(drop=False)

df = pd.read_table('c:/analysis/서울시 여름철 평균기온 위치정보.csv',  header = 0, sep = ',', encoding='euc-kr')
df['관측소명'] = df['관측소명'] + '구'
df.loc[16,'관측소명'] = '중구'
df.loc[4,'관측소명'] = '동작구'
df.loc[26,'관측소명'] = '종로구'

df = df.drop(df[df['관측소명'] == '한강구'].index)
df = df.drop(df[df['관측소명'] == '북한산구'].index)
df = df.sort_values(by = '관측소명', ascending = True)
df = df.reset_index(drop=False)

s_emds = pd.concat([df, s_emds], axis = 1)

geom = gpd.points_from_xy(s_emds['x'], s_emds['y'], crs = 'epsg:5179')
emd = gpd.GeoDataFrame(s_emds, geometry = 'geometry')

dfq = pd.read_table('c:/analysis/서울시 무더위쉼터.csv',  header = 0, sep = ',', encoding='euc-kr')

point = gpd.GeoDataFrame(dfq, geometry = gpd.points_from_xy(dfq['경도'], dfq['위도'], crs = 'epsg:4326'))
point_utm = point.to_crs(5179)

seoul_emds = gpd.read_file('c:/analysis/seoul_emd.shp')

point_utm['구'] = point_utm['도로명주소'].str.extract('(\S+)[구]')
point_utm['구'] = point_utm['구'] + '구'


_gu = list(s_emds['관측소명'])
_gu.sort()

_point = list(point_utm['구'])
_point.sort()

emd = emd.set_crs(5179)
emd.crs

emd = emd.drop(columns=['index'])

aseoul = emd.to_crs(4326)
seoul_json = aseoul.__geo_interface__

point_utm = point_utm.to_crs(4326)
point_json = point_utm.__geo_interface__


# In[202]:


#김동현

# 대피소
dfs = pd.read_table('c:/analysis/earth.csv', header=0, sep=',', encoding='euc-kr')
geom = gpd.points_from_xy(dfs['x'], dfs['y'], crs="epsg:4326")
geom_utm = geom.to_crs(5179)
shelter_point = gpd.GeoDataFrame(dfs, geometry=geom_utm)

# 시군구 
sgg = gpd.read_file('c:/analysis/sigungu.shp', encoding='utf-8')
seoul_sgg = sgg[sgg['SIG_CD'].str.startswith('11')]
seoul_sgg.crs = "EPSG:5179"

# 격자인구 (1km)
seoul_nlsp = gpd.read_file('c:/analysis/nlsp_seoul.shp')
seoul_nlsp.crs = "EPSG:5179"

# 공간조인
shelter_seoul = gpd.sjoin(shelter_point, seoul_sgg, predicate='within')
pop_nlsp_seoul = gpd.sjoin(seoul_nlsp, seoul_sgg, predicate='intersects')

# 행정구역 분류
districts = [
    ('용산구', '11170'),
    ('중구', '11140'),
    ('성동구', '11200'),
    ('광진구','11215'),
    ('동대문구','11230'),
    ('중앙구','11260'),
    ('성북구','11290'),
    ('강북구','11305'),
    ('도봉구','11320'),
    ('노원구','11350'),
    ('은평구','11380'),
    ('서대문구','11410'),
    ('마포구','11440'),
    ('양천구','11470'),
    ('강서구','11500'),
    ('구로구','11530'),
    ('금천구','11545'),
    ('영등포구','11590'),
    ('관악구','11620'),
    ('서초구','11650'),
    ('강남구','11680'),
    ('송파구','11710'),
    ('강동구','11740'),
    ('종로구', '11110')
]


# In[203]:


import folium
from folium import plugins


shel = gpd.read_file('c:/analysis/TL_FLOOD_P.shp', encoding = 'euc-kr')
shel = shel.to_crs(5179)


rain = pd.read_table('c:/analysis/seoul_rain_lonlat.csv', encoding = 'utf-8', sep = ',')

pp = gpd.points_from_xy(rain['Longitude'], rain['Latitude'], crs = '4326')
a = pp.to_crs(5179)
pa = gpd.GeoDataFrame(rain, geometry = a)

buffer_distance = 1000
pa['Buffer'] = pa['geometry'].buffer(buffer_distance)
bs = pa.copy()
bs['geometry'] = pa['geometry'].buffer(buffer_distance)


pa['kor_nm'] = pa['지번주소'].str.extract('(\S+)[구]')
pa['kor_nm'] = pa['kor_nm'] + '구'


ex = pa['지번주소']
ex['구'] = pa['지번주소'].apply(lambda x: x.split(' ')[1] if len(x.split(' ')) >= 2 else None)
ex_result = ex.groupby('구').size().reset_index(name='건수')


data1 = {'구': ['강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구', '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구',
              '성동구', '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중앙구'],
         '시군구코드': [11230, 11250, 11090, 11160, 11210, 11050, 11170, 11180, 11110, 11100, 11060, 11200, 11140, 11130,
                  11220, 11040, 11080, 11240, 11150, 11190, 11030, 11120, 11010, 11020, 11070]}
df1 = pd.DataFrame(data1)

gus = list(df1['구'])
gus.sort()


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


s_emda = gpd.GeoDataFrame.from_features(data['features'])

s_emda['adm_nm'] = s_emda['adm_nm'].str.replace('서울특별시', '')

s_emda = s_emda.sort_values(by = 'adm_nm', ascending = True)
s_emda = s_emda.reset_index(drop=False)

data2 = {'시군구코드': [11230, 11250, 11090, 11160, 11210, 11050, 11170, 11180, 11110, 11100, 11060, 11200, 11140, 11130,
                  11220, 11040, 11080, 11240, 11150, 11190, 11030, 11120, 11010, 11020, 11070],
                  '빈도': [35, 41, 4, 0, 0, 0, 64, 0, 0, 1, 0, 5, 59, 15, 70, 46, 0, 0, 9, 0, 42, 2, 1, 10, 0]}
inun_1 = pd.DataFrame(data2)

inun_2 = pd.concat([inun_1,s_emd],axis=1)
inun_2 = inun_2.drop('adm_nm',axis=1)
inun_2['kor_nm'] = ['강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구', '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구',
              '성동구', '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중앙구']

geom = gpd.points_from_xy(inun_2['x'],inun_2['y'], crs = 'epsg:5179')
inun_3 = gpd.GeoDataFrame(inun_2, geometry = inun_2['geometry'])
inun_3 = inun_3.set_crs(5179)


bseoul =inun_3.to_crs(4326)
seoul_json = bseoul.__geo_interface__


import folium

seoul_latitude = 37.5665
seoul_longitude = 126.9780

zoom_level = 11

map = folium.Map(location=[seoul_latitude, seoul_longitude], zoom_start=zoom_level)
map = bs.explore(m = map, color = '#FFA7A7', style_kwds = {'alpha' : 0.5})
shel.explore(m = map, color = '#4374D9', style_kwds = {'weight': 5})
folium.LayerControl().add_to(map)


seoul_latitude, seoul_longitude = 37.5665, 126.9780
zoom_level = 11
initial_map = folium.Map(location=[seoul_latitude, seoul_longitude], zoom_start=zoom_level)

initial_map = bs.explore(m=initial_map, color='#FFA7A7', style_kwds={'alpha': 0.5})
initial_map = shel.explore(m=initial_map, color='#4374D9', style_kwds={'weight': 2})


# In[214]:


from dash import Dash, dcc, html, Input, Output, State

# app structure
app = Dash(__name__)
app.title = ('Dashboard | Seoul Shelter Data')
server = app.server

# App layout
app.layout = html.Div([
    html.H2('서울 대피소 현황',
            style = {'textAlign': 'center', 
                     'marginBottom': 10, 
                     'marginTop': 10}),
    dcc.Tabs([
        dcc.Tab(label = '지진대피소',
               children=[html.P("(격자인구에 대한) 지진 대피소의 입지현황을 확인하고 싶은 구를 고르시오.", style = {'float':'center','marginLeft':250, 'fontWeight': 'bold'}),
    html.Div([
        dcc.Dropdown(
            id='district-dropdown',
            options=[{'label': district[0], 'value': district[1]} for district in districts],
            value=districts[0][1],
            style={'width': '30%','marginTop': 15,'margin-bottom':20, 'marginLeft':120}
        ),
        # folium map
        html.Iframe(id='folium-map', width='72%', height='600', style={'float': 'center','display': 'inline-block','marginLeft':250}),
        html.Div('출처:서울열린데이터광장 - 서울시 지진대피소 &  ngis - 서울시격자인구', style={'float':'center','textAlign': 'center', 'fontSize': '10px'})
    ])
]
               ),
        dcc.Tab(label = '침수대피소',
                children =[
                    html.Div([
                    
                        html.Div(className = 'inundation',
                                 children = [html.Div(dcc.Dropdown(id = 'gua',
                                                                   options = [{'label': i, 'value': i} for i in gus],
                                                                   value = max(gus),
                                                                   style = {'width': '45%','float':'right'})),
                                             html.Div(dcc.Graph(id = 'mapa'))
                                             ])
                            ], style = {'float': 'left', 'display': 'inline-block', 'width': '45%'}),
                        html.Div([
                            html.Iframe(id='folium-maps', width= '50%', height='500',style = {'marginTop':45}),

                            dcc.Slider(id='buffer-slider'),
                            html.Div('출처:서울열린데이터광장 - 서울시 수해대피소 공간정보 & 서울열린데이터광장 서울시 자연재해위험개선지구(침수지구) 현황', style={'float':'right','textAlign': 'center', 'fontSize': '10px','marginRight':220})
                ])]),
        dcc.Tab(label = '미세먼지대피소',
                children =[
                    html.Div([
                    
                        html.Div(className = 'PM',
                                 children = [html.Div(dcc.Graph(id = 'map'))
                                             ])
                            ], style = {'float': 'left', 'display': 'inline-block', 'width': '48%', 'marginTop': 100, 'marginLeft':50}),
                        html.Div([
                            html.Div(className = 'shelt',
                                     children = [html.P("대피소의 위치를 알고 싶은 '구'를 선택하시오.", style = {'float':'left','marginLeft':30, 'fontWeight': 'bold'}),
                                                 html.Div(dcc.Dropdown(id = 'id_gu',
                                                                       options = [{'label': i, 'value': i} for i in gu],
                                                                       value=max(gu),
                                                                       style = {'width': '45%', 'marginTop': 10,'marginLeft':20})),
                                               html.Div(dcc.Graph(id = 'shelter'))]
                                    )
                                ], style = {'float': 'right', 'width': '45%','marginRight':50}),
                    
                              ]
               ),
                dcc.Tab(label = '무더위쉼터',
                children =[
                    html.Div([
                    
                        html.Div(className = 'tem',
                                 children = [
                                             html.Div(dcc.Graph(id = 'maps'))
                                             ])
                            ], style = {'float': 'left', 'display': 'inline-block', 'width': '45%', 'marginTop': 100, 'marginLeft':50}),
                        html.Div([
                            html.Div(className = 'shelt',
                                    children = [html.P("대피소의 위치를 알고 싶은 '구'를 선택하시오.", style = {'float':'left','marginLeft':30, 'fontWeight': 'bold'}),
                                               html.Div(dcc.Dropdown(id = 'gu',
                                                                   options = [{'label': i, 'value': i} for i in _gu],
                                                                   value = max(_gu),
                                                                   style = {'width': '45%', 'marginTop': 10,'marginLeft':20})),
                                               html.Div(dcc.Graph(id = 'shelters'))]
                                    )
                                ], style = {'float': 'right', 'width': '45%','marginRight':50})
                              ]
               )
            ])
        ])


# In[215]:


def create_folium_map(district):
    district_shelter = shelter_seoul[shelter_seoul['SIG_CD'].str.startswith(district[1])]
    district_pop = pop_nlsp_seoul[pop_nlsp_seoul['SIG_CD'].str.startswith(district[1])]
    seoul_district = seoul_sgg[seoul_sgg['SIG_CD'].str.startswith(district[1])]

    m = district_pop.explore(column='val', cmap='YlOrRd', style_kwds={'weight': 0.7})
    district_shelter.explore(m=m, color='blue')
    seoul_district.boundary.explore(m=m, color='black')
    folium.LayerControl().add_to(m)

    
    return m._repr_html_()


# In[216]:


@app.callback(
    Output('folium-map', 'srcDoc'),
    [Input('district-dropdown', 'value')])
def update_folium_map(selected_district):
    selected_district = [district for district in districts if district[1] == selected_district][0]
    return create_folium_map(selected_district)


# In[217]:


@app.callback(Output('map', 'figure'),
              Input('id_gu', 'value'))
    
def update_output(val):
    
    df_map = seoul.loc[:, ['MSRSTE_NM', 'PM10']]

    df_map['text'] = df_map['MSRSTE_NM'] + ' ' + '|' + ' ' + df_map['PM10'].astype(str) + 'µg/m³'
    
    trace = go.Choroplethmapbox(geojson = seoul_json,
                                locations = df_map.index,
                                z = seoul.PM10,
                                text = df_map['text'],
                                hoverinfo = 'text',
                                
                                colorscale="YlOrRd",
                                colorbar=dict(title='PM10(µg/m³)'))

    layout = go.Layout(title = '서울 미세먼지 농도',
                       mapbox_style="open-street-map",
                       mapbox_zoom=8.5, mapbox_center = {"lat": 37.57, "lon": 127},
                              annotations=[
                           {
                               'x': 0.5,
                               'y': -0.1,
                               'xref': 'paper',
                               'yref': 'paper',
                               'text': '출처:통계지리정보서비스 행정구역경계API & 서울열린데이터광장 서울시 일별 평균 대기오염도 정보',
                               'showarrow': False,
                               'font': {'size': 10}
                           }])

    figure = go.Figure(trace, layout)
    
    return figure


# In[218]:


@app.callback(
    Output('shelter', 'figure'),
    [Input('id_gu', 'value')]
)

def update_output(val):
    
    place = seoul_shel.loc[seoul_shel['구'] == val]
    place = place.loc[:,['대피소 명칭', '대피소 상세주소', '최대수용가능인원', 'Latitude', 'Longitude', '구']]
    
    place['text'] = place['대피소 상세주소'] + ' ' + '|' + ' ' + place['최대수용가능인원'].astype(str) + '명'    

    #fig = px.scatter_mapbox(place, lat='Latitude', lon='Longitude',text = place['text'])
    
#    layout = fig.update_layout(title = 'Shelter',
#                              mapbox_style="open-street-map",
#                               mapbox_zoom=9,
#                               mapbox_center={'lat': 37.6, 'lon': 127}
#    )
    
#    figure = go.Figure(fig, layout)
     
    shelter_trace = go.Scattermapbox(
        lat=place['Latitude'],
        lon=place['Longitude'],
        mode='markers',
        marker=dict(size = 2.5 * np.sqrt(place['최대수용가능인원']),
                    color='blue',  # 포인트의 색깔 설정
                    symbol='circle',  # 포인트의 모양 설정
                    opacity=0.7),
        text=place['text']
    )

    shelter_layout = go.Layout(
        title=f'대피소의 개수 : {len(place)}개',
        mapbox_style="open-street-map",
        mapbox_zoom=11.2,
        mapbox_center={'lat': place['Latitude'].mean(), 'lon': place['Longitude'].mean()},
        annotations=[
                           {
                               'x': 0.5,
                               'y': -0.1,
                               'xref': 'paper',
                               'yref': 'paper',
                               'text': '출처:서울열린데이터광장 - 서울시미세먼지대피소',
                               'showarrow': False,
                               'font': {'size': 10}
                           }]
    )

    figure = go.Figure(shelter_trace, shelter_layout)
    
    return figure


# In[219]:


@app.callback(Output('maps', 'figure'),
              Input('gu', 'value'))
    
def update_output(val):
    
    df_map = aseoul.loc[:, ['관측소명', '평균기온']]

    df_map['text'] = df_map['관측소명'] + \
                     df_map['평균기온'].astype(str) + '℃'
    
    trace = go.Choroplethmapbox(geojson = seoul_json,
                                locations = df_map.index,
                                z = df_map['평균기온'],
                                text = df_map['text'],
                                hoverinfo = 'text',
                                colorscale="YlOrRd",
                                colorbar=dict(title='(℃)'))

    layout = go.Layout(title = '서울 여름철 평균 기온',
                   mapbox_style="open-street-map",
                   mapbox_zoom=8.5, mapbox_center = {"lat": 37.57, "lon": 127},
                                                    annotations=[
                           {
                               'x': 0.5,
                               'y': -0.1,
                               'xref': 'paper',
                               'yref': 'paper',
                               'text': '출처:통계지리정보서비스 행정구역경계API & 서울시 여름철 평균기온 위치정보',
                               'showarrow': False,
                               'font': {'size': 10}
                           }])

    figure = go.Figure(trace, layout)
    
    return figure


# In[220]:


@app.callback(Output('shelters','figure'),
             Input('gu','value'))

def update_output(val):
    
    place = point_utm.loc[point_utm['구'] == val]
    place = place.loc[:,['쉼터명칭','도로명주소','지번상세주소','구','X좌표','이용가능인원','Y좌표','경도','위도']]
    
    place['text'] = place['도로명주소'] + ' ' + '|' + ' ' + place['쉼터명칭'].astype(str)     

    
    shelter_trace = go.Scattermapbox(
        lat=place['위도'],
        lon=place['경도'],
        mode='markers',
        marker=dict(size=np.sqrt(place['이용가능인원']),
                    color='blue',
                    symbol='circle',
                    opacity=0.7),
        text=place['text']
    )

    shelter_layout = go.Layout(
        title=f'대피소의 개수 : {len(place)}개',
        mapbox_style="open-street-map",
        mapbox_zoom=10.5,
        mapbox_center={'lat': place['위도'].mean(), 'lon': place['경도'].mean()},
                annotations=[
                           {
                               'x': 0.5,
                               'y': -0.1,
                               'xref': 'paper',
                               'yref': 'paper',
                               'text': '출처:서울열린데이터광장 - 서울시 무더위심터',
                               'showarrow': False,
                               'font': {'size': 10}
                           }]
    )

    figure = go.Figure(shelter_trace, shelter_layout)
    
    
    return figure


# In[221]:


# 서울시 구별 침수 피해 빈도수
@app.callback(Output('mapa', 'figure'),
              Input('gua', 'value'))
    
def update_output(val):
    
    df_map = inun_3
    df_map['text'] = inun_3['빈도'].astype(str) + '회'
    
    trace = go.Choroplethmapbox(geojson = seoul_json ,
                                locations = df_map.index,
                                z = df_map.빈도,
                                text = df_map['text'],
                                hoverinfo = 'text',
                                
                                colorscale="YlOrRd",
                                colorbar=dict(title='빈도수'))

    layout = go.Layout(title = '서울 저층주거 침수피해 빈도',
                       mapbox_style="open-street-map",
                       mapbox_zoom=9, mapbox_center = {"lat": 37.5665, "lon": 127},
                                      annotations=[
                           {
                               'x': 0.5,
                               'y': -0.1,
                               'xref': 'paper',
                               'yref': 'paper',
                               'text': '출처:통계지리정보서비스 행정구역경계API & 서울열린데이터광장 서울시 자연재해위험개선지구(침수지구) 현황',
                               'showarrow': False,
                               'font': {'size': 10}
                           }])

    figure = go.Figure(trace, layout)
    
    return figure


# In[222]:


# 서울시 침수지역 + 대피소 위치
@app.callback(
    Output('folium-maps', 'srcDoc'),
    [Input('buffer-slider', 'value')]
)
def update_map(buffer_distance):
    # Create a new Folium map
    updated_map = folium.Map(location=[seoul_latitude, seoul_longitude], zoom_start=zoom_level)

    # Explore bs and shel on the updated map
    updated_map = bs.explore(m=updated_map, color='#FFA7A7', style_kwds={'alpha': 1, 'fillOpacity': 0.3})
    updated_map = shel.explore(m=updated_map, color='#4374D9', style_kwds={'weight': 5})

    # Add LayerControl to switch layers on/off
    #folium.LayerControl().add_to(updated_map)
    
    folium.TileLayer('cartodbpositron').add_to(updated_map)

    return updated_map._repr_html_()


# In[223]:


if __name__=='__main__':
    app.run_server(debug = False)

