#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 27 13:00:08 2022

@author: zidong
"""
# os.getcwd()
# os.chdir("/Users/zidong/Documents/GitHub/503-final-project")

import pandas as pd
import numpy as np
import os

from bokeh.io import curdoc
from bokeh.layouts import layout
from bokeh.models import (Button, CategoricalColorMapper, ColumnDataSource,
                          HoverTool, Label, SingleIntervalTicker, Slider)
from bokeh.palettes import Spectral7
from bokeh.plotting import figure


gdp = pd.read_csv("data/GDP by country.csv",skiprows=4)

Country_Code = pd.DataFrame(gdp,columns=(['Country Name','Country Code']))

gdp = gdp.drop(['Indicator Name','Indicator Code','Country Name'], 1)
gdp = gdp.set_index(['Country Code'], drop=True)

pop = pd.read_csv("data/Population by country.csv",skiprows=4)
pop = pop.drop(['Indicator Name','Indicator Code','Country Name'], 1)
pop = pop.set_index(['Country Code'], drop=True)

medal_count = pd.read_csv("data/Summer_Olympic_medallists.csv")
medal_count = medal_count.groupby(['NOC','Edition']).size().reset_index(name='medal number')
medal_count = medal_count.rename(columns = {'NOC':'Country Code','Edition':'Year'})
medal_count = medal_count.pivot(index='Country Code', columns='Year', values='medal number')

regions = pd.read_csv("data/Regions.csv")

# Filter years that have both median_count, gdp and pop data
year_list = medal_count.columns.values
year_list = list(filter(lambda x:x>=1960,year_list))

print(type(year_list[1]))

# Convert the filtered years into string type to facilitate the processing of the original data set
year_list_str = [str(x) for x in year_list]

print(year_list_str)

gdp = gdp[year_list_str]
pop = pop[year_list_str]

medal_count = medal_count[year_list]
medal_count.columns = year_list_str


# For rows
rownames =pd.DataFrame(medal_count.index) 
rownames2 = pd.DataFrame(gdp.index)
rownames3 = pd.DataFrame(pop.index)

result = pd.merge(rownames, rownames2, on='Country Code')
result = pd.merge(result, rownames3, on='Country Code')

gdp = pd.merge(result, gdp, on='Country Code')
gdp = pd.merge(Country_Code, gdp, on='Country Code')
gdp.rename({'Country Name':'Country'}, axis='columns', inplace=True)
gdp = gdp.drop(['Country Code'], axis=1)
gdp = gdp.set_index(['Country'])

pop = pd.merge(result, pop, on='Country Code')
pop = pd.merge(Country_Code, pop, on='Country Code')
pop.rename({'Country Name':'Country'}, axis='columns', inplace=True)
pop = pop.drop(['Country Code'], axis=1)
pop = pop.set_index(['Country'])

medal_count = pd.merge(result, medal_count, on='Country Code')
medal_count = pd.merge(Country_Code, medal_count, on='Country Code')
medal_count.rename({'Country Name':'Country'}, axis='columns', inplace=True)
medal_count = medal_count.drop(['Country Code'], axis=1)
medal_count = medal_count.set_index(['Country'])


columns = list(gdp.columns)
years = year_list 
rename_dict = dict(zip(columns, years))

gdp = gdp.rename(columns=rename_dict)
medal_count = medal_count.rename(columns=rename_dict)
pop = pop.rename(columns=rename_dict)

# Turn population into bubble sizes. Use min_size and factor to tweak.
scale_factor = 200
pop_size = np.sqrt(pop / np.pi) / scale_factor
min_size = 3
pop = pop_size.where(pop_size >= min_size).fillna(min_size)


regions = regions.rename(columns=rename_dict)
regions.rename({'Country Name':'Country'}, axis='columns', inplace=True)
regions.rename({'Regions':'region'}, axis='columns', inplace=True)

regions = pd.merge(regions, medal_count, on='Country')
regions = regions[['Country','region','ID']]

regions_df = regions.set_index(['Country','ID'])
regions_list = list(regions_df['region'].unique())

# print(type(regions_df["region"]))

df = pd.concat({'medal count': medal_count,
                'gdp': gdp,
                'pop': pop},
               axis=1, join="outer")

data = {}


for year in years:
    df_year = df.iloc[:,df.columns.get_level_values(1)==year]
    df_year.columns = df_year.columns.droplevel(1)
    data[year] = df_year.join(regions_df.region).reset_index().to_dict('series')

source = ColumnDataSource(data=data[years[0]])


# print(df_year.max())
plot = figure(title='Olympic Data', height=300)
#plot.xaxis.ticker = SingleIntervalTicker(interval=1)
plot.xaxis.axis_label = "Medal count"
#plot.yaxis.ticker = SingleIntervalTicker(interval=20)
plot.yaxis.axis_label = "gdp"

label = Label(x=1.1, y=18, text=str(years[0]), text_font_size='93px', text_color='#eeeeee')
plot.add_layout(label)

color_mapper = CategoricalColorMapper(palette=Spectral7, factors=regions_list)

plot.circle(
    x='medal count',
    y='gdp',
    size='pop',
    source=source,
    fill_color={'field': 'region', 'transform': color_mapper},
    fill_alpha=0.8,
    line_color='#7c7e71',
    line_width=0.5,
    line_alpha=0.5,
    legend_group='region',
)


plot.add_tools(HoverTool(tooltips="@Country", show_arrow=False, point_policy='follow_mouse'))

def animate_update():
    year = slider.value + 4
    if year > years[-1]:
        year = years[0]
    slider.value = year


def slider_update(attrname, old, new):
    year = slider.value
    label.text = str(year)
    source.data = data[year]

slider = Slider(start=years[0], end=years[-1], value=years[0], step=4, title="Year")
slider.on_change('value', slider_update)

callback_id = None

def animate():
    global callback_id
    if button.label == '► Play':
        button.label = '❚❚ Pause'
        callback_id = curdoc().add_periodic_callback(animate_update, 200)
    else:
        button.label = '► Play'
        curdoc().remove_periodic_callback(callback_id)

button = Button(label='► Play', width=60)
button.on_event('button_click', animate)

layout = layout([
    [plot],
    [slider, button],
], sizing_mode='scale_width')


curdoc().add_root(layout)
curdoc().title = "Olympic Data"

