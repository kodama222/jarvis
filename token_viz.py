import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os 

gmt_url = 'https://raw.githubusercontent.com/kodama222/jarvis/main/data/gmt.csv'
sxp_url = 'https://raw.githubusercontent.com/kodama222/jarvis/main/data/sxp.csv'

urls = [gmt_url, sxp_url]

data_dict = {}

token_names = {'GMT', 'SXP'}

for u in urls:
    
    # take file name
    f0 = os.path.basename(u)
    f1 = f0.rsplit('.')[0]
    
    # read the csv file      
    df = pd.read_csv(u)
    
    # convert date column to datetime and sort by date
    df['date'] = pd.to_datetime(df['date'], infer_datetime_format=True)
    df = df.sort_values(by=['date'], ignore_index=True)
    df = df.set_index('date')
    
    df = df.apply(pd.to_numeric)
    
    # create dict entry with dataframe as value and filename as key
    data_dict[f1] = df
    
data = list(data_dict.values())

def main():
    
    st.markdown(
    """
    # **Token Supply Distrbution**
    """
    )
    
    token = st.sidebar.selectbox(
     'What token do you want to know more about?',
     ('GMT', 'SXP'))
    
    if token == 'SXP':
        df = data['SXP']
        
    elif token == 'GMT':
        
    
    option = st.sidebar.selectbox(
     'What kinda chart do you want to see?',
     ('All Holders', 'Insiders vs Non-Insiders'))
    
    if option == 'All Holders':
        
        return
    
    elif option == 'Insiders vs Non-Insiders':
        
        return

if __name__ == "__main__":
    st.set_page_config(
        page_title='Apecoin Supply Distribution Tracker'
    )
    main()