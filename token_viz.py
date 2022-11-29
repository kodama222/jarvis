import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

gmt_url = (
    'https://raw.githubusercontent.com/kodama222/jarvis/main/data/gmt.csv'
)
sxp_url = (
    'https://raw.githubusercontent.com/kodama222/jarvis/main/data/sxp.csv'
)

urls = [gmt_url, sxp_url]

data_dict = {}

token_names = {'GMT', 'SXP'}

for u in urls:

    # take file name
    f0 = os.path.basename(u)
    f1 = f0.rsplit('.')[0].upper()

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
    # **Token Supply Distribution**
    """
    )

    token = st.sidebar.selectbox(
        'What token do you want to know more about?', ('GMT', 'SXP')
    )

    all_final_dist = (
        data_dict[token].drop(columns=['insiders', 'non-insiders']).iloc[-1]
    )
    in_vs_nonin_final = data_dict[token][['insiders', 'non-insiders']].iloc[-1]

    option = st.sidebar.selectbox(
        'What kinda chart do you want to see?',
        ('All Holders', 'Insiders vs Non-Insiders'),
    )

    if option == 'All Holders':

        # plotly pie chart of final token distribution
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=all_final_dist.index, values=all_final_dist.values
                )
            ]
        )
        fig.update_traces(
            textinfo='percent+label'
        )   # remove to show only % label on chart
        fig.update_layout(title_text=f'{token} Allocation', title_x=0.5)

        st.plotly_chart(fig, use_container_width=True)

        # stacked area chart of supply distribution
        fig = px.area(
            data_dict[token].drop(columns=['insiders', 'non-insiders'])
        )
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Token Supply',
            legend_title='Holders',
            plot_bgcolor='rgba(0, 0, 0, 0)',
        )

        st.plotly_chart(fig, use_container_width=True)

        # Evolution of supply distribution %
        fig = px.area(
            data_dict[token].drop(columns=['insiders', 'non-insiders']),
            title=f'{token} Supply %',
            groupnorm='fraction',
        )
        fig.update_layout(
            yaxis=dict(showgrid=True, gridcolor='rgba(166, 166, 166, 0.35)'),
            yaxis_tickformat=',.0%',
            xaxis=dict(showgrid=False, gridcolor='rgba(166, 166, 166, 0.35)'),
            xaxis_title='Date',
            yaxis_title='Token Supply',
            legend_title='Holders',
            plot_bgcolor='rgba(0, 0, 0, 0)',
            autosize=False,
            width=1000,
            height=550,
            title_x=0.4,
        )

        st.plotly_chart(fig, use_container_width=True)

        return

    elif option == 'Insiders vs Non-Insiders':

        # plotly pie chart of final token distribution
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=in_vs_nonin_final.index,
                    values=in_vs_nonin_final.values,
                )
            ]
        )
        fig.update_traces(
            textinfo='percent+label'
        )   # remove to show only % label on chart
        fig.update_layout(title_text=f'{token} Allocation', title_x=0.5)

        st.plotly_chart(fig, use_container_width=True)

        # stacked area chart of supply distribution
        fig = px.area(data_dict[token][['insiders', 'non-insiders']])
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Token Supply',
            legend_title='Holders',
            plot_bgcolor='rgba(0, 0, 0, 0)',
        )

        st.plotly_chart(fig, use_container_width=True)

        # Evolution of supply distribution %
        fig = px.area(
            data_dict[token][['insiders', 'non-insiders']],
            title=f'{token} Supply %',
            groupnorm='fraction',
        )
        fig.update_layout(
            yaxis=dict(showgrid=True, gridcolor='rgba(166, 166, 166, 0.35)'),
            yaxis_tickformat=',.0%',
            xaxis=dict(showgrid=False, gridcolor='rgba(166, 166, 166, 0.35)'),
            xaxis_title='Date',
            yaxis_title='Token Supply',
            legend_title='Holders',
            plot_bgcolor='rgba(0, 0, 0, 0)',
            autosize=False,
            width=1000,
            height=550,
            title_x=0.4,
        )

        st.plotly_chart(fig, use_container_width=True)

        return


if __name__ == '__main__':
    st.set_page_config(page_title='Supply Distribution Tracker')
    main()
