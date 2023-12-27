# -*- coding: utf-8 -*-
"""
Created on Wed December 20 2023

@author: eswhitehead-zimmers
"""

import geopandas as gp
import folium as fl
from streamlit_folium import st_folium
import streamlit as st
import pandas as pd
import plotly.express as px


def load_dat():
# This function loads in gw latlong 
    trends_all_sites = pd.read_csv("sw_trends_all_sites.csv",
                                   index_col = 0,
                                   dtype = {"site_no": "string"})
    
    site_nos = trends_all_sites['site_no'].unique()
    
    return trends_all_sites, site_nos

def plot_dat(trends_all_sites, station_nm):
# This function plots mann-kendall slope for each percentile of a given site
# Input:
    # trends_all_sites: variable containing all trends for all 76 sites
    # site_no: site number for the site you want trends plotted for. Note:
        # should be given as a string.
# Output:
    # plots trends for specified site_no
      
    # filter out which specific site you want to plot
    trends_all_sites = trends_all_sites[trends_all_sites['station_nm'] == station_nm]
    
    # Create title including site no (which is variable)  
    titl_for_plot = 'Annual water level percentile trends for ' + station_nm
    
    # pretty close to final figure:
    fig = px.line(trends_all_sites, y = 'slope', x = 'percentile', color = 'Trend')
    fig.update_traces(mode='markers')
    fig.add_hline(y=0, line_width=3, line_dash="solid", line_color="green")
    fig.update_layout(
        title_text= titl_for_plot, 
        yaxis=dict(title='slope of trend (%)'),
        xaxis=dict(title='Groundwater Level Percentile'),
        autosize = True)


    return(fig)

def get_pos(lat, lng):
    return lat, lng
    
def getgeodf(trends_all_sites):
    
    df = pd.DataFrame(
        {
        "station_nm": [],
        "lat": [],
        "long": []
        }
    )
    
    for station_nm in trends_all_sites["station_nm"]:
        df["station_nm"] = trends_all_sites["station_nm"]
        df["lat"] = trends_all_sites["lat"]
        df["long"] = trends_all_sites["long"]
    
    gdf = gp.GeoDataFrame(df,
                          geometry=gp.points_from_xy(df.long, df.lat),
                          crs=4326)
    
    return gdf

def choose_site(latlong, gdf):
    
    ### Make sure all the sites have the same precision for lat/long
    # Round data we have in geodataframe
    gdf.lat = gdf.lat.round(decimals = 4)
    gdf.long = gdf.long.round(decimals = 4)
    
    # Round latlong data from user
    # Put latlong into data frame so we have consistent rounding between user and gdf
    latlong_df = pd.DataFrame(
        {
        "lat": [latlong[0]],
        "long": [latlong[1]]
        }
    )
    
    # Round latlong
    latlong_df.lat = latlong_df.lat.round(decimals = 4)
    latlong_df.long = latlong_df.long.round(decimals = 4)
    
    
    # create counter variable for loop
    i = 0
    
    # Set option to zero for when user clicks a point that isn't a site
    option = 0

    
    for station_nm in gdf.station_nm:
        
        if (latlong_df.lat[0] == gdf["lat"][i] and latlong_df.long[0] == gdf["long"][i]):
            option = station_nm
        
        i = i + 1
        
    return option

### App Layout ###
# Adjust layout to take up full width of screen
st.set_page_config(layout="wide")

# Add Title
'''
# Discharge Trends for Streams in Deleware River Basin
'''

# Separate layout into two columns 1) map 2) trends plot
col1, col2 = st.columns(2)


### LOAD IN DATA ###
# Trends data
trends_all_sites, site_nos = load_dat()

# Initialize coordinates user will choose
latlong = 0,0




### CREATE INTERACTIVE MAP ###
# Put map in column 1
with col1:
    # Create interactive map
    m = fl.Map(location=[40.9, -75], zoom_start=6.55)
    
    # Create a geopandas latlong frame so we can create interactive dots using geopandas
    gdf = getgeodf(trends_all_sites)
    
    # This function creates clickable dots
    gdf.explore(
        m = m,
        color = "red",
        marker_kwds=dict(radius=8, fill=True),
        tooltip="station_nm",
        tooltip_kwds=dict(labels=False),
        name="station_nm"
         )
    
    # This produces the map in streamlit. This HAS TO COME AFTER THE MAP IS FINISHED
    gw = st_folium(m, use_container_width = True)



### GET USER INPUT ###
# If the user clicks, pull lat long values of click
if gw.get("last_clicked"):
    # Store lat/long vals from user
    latlong = get_pos(gw["last_clicked"]["lat"], gw["last_clicked"]["lng"])

### PLOT TRENDS FIGURE ### 
# Put the trends plot in column 2
with col2:
    # See if lat long selection matches a site and then produce trends plot for that site
    if latlong is not None:
        option = choose_site(latlong, gdf)
        if option != 0:
            fig = plot_dat(trends_all_sites, option)
            st.plotly_chart(fig, use_container_width = True)
            st.write("The quantile Mann-Kendall method was applied to daily discharge data from streams in the Deleware River Basin.")
        else: 
            '''
            Choose a USGS site to get started
            '''

    


    
    


    
    
    
