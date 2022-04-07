
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 23:54:08 2022

@author: zidong
"""

import plotly.express as px
import pandas as pd
import numpy as np


# load data
gdp = pd.read_csv("data/GDP by country.csv",skiprows=4)

# clean data
gdp = gdp.drop(['Indicator Name','Indicator Code','Country Name'], 1)

# wide to long
gdp = pd.melt(gdp, id_vars=['Country Code'], value_vars=list(gdp.columns[1:]),
              var_name='Year', value_name='GDP')


pop = pd.read_csv("data/Population by country.csv",skiprows=4)
pop = pop.drop(['Indicator Name','Indicator Code','Country Name'], 1)
pop = pd.melt(pop, id_vars=['Country Code'], value_vars=list(pop.columns[1:]),
              var_name='Year', value_name='POP')

medal_count = pd.read_csv("data/Summer_Olympic_medallists.csv")
medal_count = medal_count.groupby(['NOC','Edition']).size().reset_index(name='medal number')
medal_count = medal_count.rename(columns = {'NOC':'Country Code','Edition':'Year'})

regions = pd.read_csv("data/Regions.csv")
regions.columns = ['Country Name','Regions','Country Code']

# before merge, check columns type
gdp.dtypes
medal_count.dtypes

gdp['Year'] = gdp['Year'].astype('int')

# merge dataframes
merge = pd.merge(gdp, medal_count)
merge = pd.merge(regions, merge, how="inner", on=['Country Code'])



# Vis

df = merge[merge['Year']==2008]

fig = px.treemap(df, path=[px.Constant("world"), 'Regions', 'Country Name'], values='GDP',
                 color='medal number',
                 color_continuous_scale='RdBu',
                 color_continuous_midpoint=np.average(df['medal number'], weights=df['GDP']))

fig.update_layout(margin = dict(t=50, l=25, r=25, b=25), title="Number of medals won by country")
fig.show()
fig.write_html("fig2.html")












