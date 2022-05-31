import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


DATA_URL = 'https://raw.githubusercontent.com/kodama222/jarvis/main/data/apecoin_distribution.csv'
DATA_PATH = '/Users/danielroyo2227/kodama/kodama222/jarvis/data/apecoin_distribution.csv'

#@st.cache
def load_data():

    ape = pd.read_csv(DATA_URL).drop(columns=['Month'])
    
    ## DATA WRANGLING
    
    ape.Date = pd.to_datetime(ape['Date'], infer_datetime_format=True)
    ape = ape.set_index('Date')
    
    token_final_dist = ape.drop(columns=['Total', 'New Supply', 'Annual Inflation']).iloc[-1]
    
    ape['MoM Inflation'] = ape.Total.pct_change()
    
    ape_holders = ape.drop(columns=['Total', 'New Supply', 'Annual Inflation', 'MoM Inflation'])

    ape['Insiders'] = ape.drop(columns=['BAYC Holders', 'Total', 'New Supply', 'MoM Inflation', 
                                    'Annual Inflation', 'Jane Goodall L. Foundation']).sum(axis=1)
    ape['Non-Insiders'] = ape[['BAYC Holders', 'Jane Goodall L. Foundation']].sum(axis=1)
    
    in_nonin_final_dist = ape[['Insiders', 'Non-Insiders']].iloc[-1]
               
    return ape, ape_holders, token_final_dist, in_nonin_final_dist

## STREAMLIT CONFIG

def main():
    
    st.markdown(
    """
    # **Apecoin Tokenomics**
    """
    )
    
    option = st.selectbox(
     'What kinda chart do you want to see?',
     ('All Holders', 'Insiders vs Non-Insiders'))
    
    ape, ape_holders, token_final_dist, in_nonin_final_dist = load_data()

    token_name = "APE"

    if option == 'All Holders':
        
        # plotly pie chart of final token distribution
        fig = go.Figure(data=[go.Pie(labels=token_final_dist.index, values=token_final_dist.values)])
        fig.update_traces(textinfo='percent+label') # remove to show only % label on chart
        fig.update_layout(title_text=f'{token_name} Allocation', title_x=0.5)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # stacked area chart of supply distribution
        fig = px.area(ape_holders)
        fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Token Supply',
        legend_title='Holders',
        plot_bgcolor= 'rgba(0, 0, 0, 0)')

        st.plotly_chart(fig, use_container_width=True)
        
        # Evolution of supply distribution %
        fig = px.area(ape.drop(columns=['Total', 'New Supply', 'Annual Inflation']),
                    title=f"{token_name} Supply %",
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
        
    elif option == 'Insiders vs Non-Insiders':
        
        # in_nonin_final_dist
        
        # plotly pie chart of final token distribution
        fig = go.Figure(data=[go.Pie(labels=in_nonin_final_dist.index, values=in_nonin_final_dist.values)])
        fig.update_traces(textinfo='percent+label') # remove to show only % label on chart
        fig.update_layout(title_text=f'{token_name} Allocation', title_x=0.5)

        st.plotly_chart(fig, use_container_width=True)

        # stacked area chart of supply distribution
        fig = px.area(ape[['Insiders', 'Non-Insiders']])
        fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Token Supply',
        legend_title='Holders',
        plot_bgcolor= 'rgba(0, 0, 0, 0)',
        )

        st.plotly_chart(fig, use_container_width=True)
                
        # Evolution of supply distribution %
        fig = px.area(ape[['Insiders', 'Non-Insiders']],
                    title=f"{token_name} Supply %",
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

    #new and cumulative supply combined 

    ape.iloc[0, 9] = 0        # replace '-' with 0 in first row
    ape = ape.astype({"New Supply": float})

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=ape.index, y=ape['New Supply'],
        name="New Monthly Supply"
    ))
    fig.add_trace(go.Scatter(
        x=ape.index, y=ape['New Supply'].cumsum(),
        name="Cumulative New Supply",
        yaxis="y2"
    ))
                
    fig.update_xaxes(tickangle=45)
    fig.update_layout(
        yaxis=dict(
            title="New Monthly Supply",
            titlefont=dict(
                color="#1f77b4"
            ),
            tickfont=dict(
                color="#1f77b4"
            ),
            autotypenumbers='convert types',
            showgrid=True, 
            gridcolor='rgba(166, 166, 166, 0.35)',
        ),
        yaxis2=dict(
            title="Cumulative New Supply",
            titlefont=dict(
                color="#d62728"
            ),
            tickfont=dict(
                color="#d62728"
            ),
            anchor="x",
            overlaying="y",
            side="right",
        ),
        showlegend=False,
        plot_bgcolor='white',
        autosize=False,
        width=800,
        height=550,
        title_x=0.5
    )

    st.plotly_chart(fig, use_container_width=True)
    
if __name__ == "__main__":
    st.set_page_config(
        page_title='Apecoin Supply Distribution Tracker'
    )
    main()
 