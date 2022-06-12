import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os 

capcoin_url = 'https://raw.githubusercontent.com/kodama222/jarvis/main/data/capcoin.csv'
gmt_url = 'https://raw.githubusercontent.com/kodama222/jarvis/main/data/gmt.csv'
matic_url = 'https://raw.githubusercontent.com/kodama222/jarvis/main/data/matic.csv'
monthcoin_url = 'https://raw.githubusercontent.com/kodama222/jarvis/main/data/monthcoin.csv'
quartercoin_url = 'https://raw.githubusercontent.com/kodama222/jarvis/main/data/quartercoin.csv'

urls = [capcoin_url, gmt_url, matic_url, monthcoin_url, quartercoin_url]

data_dict = {}
dist_dict = {}
supply_dict = {}
totalsupply_dict = {}


def distribution_type(x, df_distribution, df_data):
    if df_distribution[x.name][2] == 'percentage':
        return x
    elif df_distribution[x.name][2] == 'amount':
        return x/df_data.start_tokens[0]*100
    
for u in urls:
    
    # take file name
    f0 = os.path.basename(u)
    f1 = f0.rsplit('.')[0].upper()
    
    ## READ DATA
    # general data    
    df_data = pd.read_csv(p, skiprows=[0], nrows=1)
    
    # distribution data
    df_distribution = pd.read_csv(p, skiprows=[0,1,2,3])
    
    # supply for entities based on data from above 
    supply = df_distribution.iloc[6:]
    dates = pd.date_range(start=df_data.start_date[0], 
                        periods=len(supply), freq=df_data.emission_schedule[0]) # calculate datetime 
    supply = supply.set_index(dates).drop(columns='entity') # set index as date
    supply = supply.astype(float)
    supply = supply.apply(lambda x : distribution_type(x, df_distribution, df_data))

    # classify entities 
    df_distribution = df_distribution.drop(columns='entity')
    team = df_distribution.iloc[3] == 'treasury'
    investors = df_distribution.iloc[3] == 'investor'
    public = df_distribution.iloc[3] == 'public'

    team_df = supply[supply.columns[team.values]]
    investors_df = supply[supply.columns[investors.values]]
    public_df = supply[supply.columns[public.values]]

    # total supply (including )
    totalsupply = pd.concat([supply, team_df.sum(axis=1), 
                    investors_df.sum(axis=1), public_df.sum(axis=1)], axis=1)
    totalsupply = totalsupply.rename(columns={0:'devs', 1:'investors', 2:'plebs'})
    
    # create dict entry with dataframe as value and filename as key
    data_dict[f1] = df_data
    dist_dict[f1] = df_distribution
    supply_dict[f1] = supply
    totalsupply_dict[f1] = totalsupply
    
    
data = list(data_dict.values())

def main():
    
    st.markdown(
    """
    # **Token Supply Distribution**
    """
    )
    
    token = st.sidebar.selectbox(
     'What token do you want to know more about?',
     ('GMT', 'SXP'))
    
    all_initial_allo = data_dict[token].drop(columns=['devs', 'investors', 'plebs']).iloc[-1]
    parties_initial_allo = data_dict[token][['devs', 'investors', 'plebs']].iloc[-1]
    
    option = st.sidebar.selectbox(
     'What kinda chart do you want to see?',
     ('All Holders', 'Different Parties'))
    
    if option == 'All Holders':
        
        # plotly pie chart of final token distribution
        fig = go.Figure(data=[go.Pie(labels=all_initial_allo.index, values=all_initial_allo.values)])
        fig.update_traces(textinfo='percent+label') # remove to show only % label on chart
        fig.update_layout(title_text=f'{token} Allocation', title_x=0.5)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # stacked area chart of supply distribution
        fig = px.area(data_dict[token].drop(columns=['devs', 'investors', 'plebs']))
        fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Token Supply',
        legend_title='Holders',
        plot_bgcolor= 'rgba(0, 0, 0, 0)')

        st.plotly_chart(fig, use_container_width=True)
        
        # Evolution of supply distribution %
        fig = px.area(data_dict[token].drop(columns=['devs', 'investors', 'plebs']),
                    title=f"{token} Supply %",
                    groupnorm='fraction')
        fig.update_layout(
            yaxis=dict(
                    showgrid=True, 
                    gridcolor='rgba(166, 166, 166, 0.35)'),
            yaxis_tickformat=',.0%',
            xaxis=dict(
                    showgrid=False, 
                    gridcolor='rgba(166, 166, 166, 0.35)'),
            xaxis_title='Date',
            yaxis_title='Token Supply',
            
            legend_title='Holders',
            plot_bgcolor= 'rgba(0, 0, 0, 0)',

            autosize=False,
            width=1000,
            height=550,
            title_x=0.4
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        return
    
    elif option == 'Insiders vs Non-Insiders':
        
        # plotly pie chart of final token distribution
        fig = go.Figure(data=[go.Pie(labels=parties_initial_allo.index, values=parties_initial_allo.values)])
        fig.update_traces(textinfo='percent+label') # remove to show only % label on chart
        fig.update_layout(title_text=f'{token} Allocation', title_x=0.5)

        st.plotly_chart(fig, use_container_width=True)

        # stacked area chart of supply distribution
        fig = px.area(data_dict[token][['devs', 'investors', 'plebs']])
        fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Token Supply',
        legend_title='Holders',
        plot_bgcolor= 'rgba(0, 0, 0, 0)',
        )

        st.plotly_chart(fig, use_container_width=True)
                
        # Evolution of supply distribution %
        fig = px.area(data_dict[token][['devs', 'investors', 'plebs']],
                    title=f"{token} Supply %",
                    groupnorm='fraction')
        fig.update_layout(
            yaxis=dict(
                    showgrid=True, 
                    gridcolor='rgba(166, 166, 166, 0.35)'),
            yaxis_tickformat=',.0%',
            xaxis=dict(
                    showgrid=False, 
                    gridcolor='rgba(166, 166, 166, 0.35)'),
            xaxis_title='Date',
            yaxis_title='Token Supply',
            
            legend_title='Holders',
            plot_bgcolor= 'rgba(0, 0, 0, 0)',

            autosize=False,
            width=1000,
            height=550,
            title_x=0.4
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        return

if __name__ == "__main__":
    st.set_page_config(
        page_title='Supply Distribution Tracker'
    )
    main()