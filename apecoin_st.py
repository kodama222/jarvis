import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


DATA_URL = 'https://raw.githubusercontent.com/kodama222/jarvis/main/data/apecoin_distribution.csv'
DATA_PATH = '/Users/danielroyo2227/kodama/kodama222/jarvis/data/apecoin_distribution.csv'


@st.cache
def load_data():

    ape = pd.read_csv(DATA_URL).drop(columns=['Month'])

    ape.Date = pd.to_datetime(ape['Date'], infer_datetime_format=True)
    ape = ape.set_index('Date')

    ape['MoM Inflation'] = ape.Total.pct_change()

    ape_holders = ape.drop(
        columns=['Total', 'New Supply', 'Annual Inflation', 'MoM Inflation']
    )

    ape['Insiders'] = ape.drop(
        columns=[
            'BAYC Holders',
            'Total',
            'New Supply',
            'MoM Inflation',
            'Annual Inflation',
            'Jane Goodall L. Foundation',
        ]
    ).sum(axis=1)
    ape['Non-Insiders'] = ape[
        ['BAYC Holders', 'Jane Goodall L. Foundation']
    ].sum(axis=1)

    ape_insiders = ape_holders.drop(
        columns=['BAYC Holders', 'Jane Goodall L. Foundation']
    )
    ape_non_insiders = ape_holders[
        ['BAYC Holders', 'Jane Goodall L. Foundation']
    ]

    ape2 = pd.concat(
        [ape_insiders, ape_non_insiders],
        keys=['Insiders', 'Non Insiders'],
        axis=1,
    )

    return ape, ape_holders, ape_insiders, ape_non_insiders


## STREAMLIT CONFIG


def main():

    st.markdown(
        """
    # **Apecoin Supply Distribution**
    """
    )

    ape, ape_holders, ape_insiders, ape_non_insiders = load_data()

    option = st.selectbox(
        'What kinda chart do you want to see?',
        ('All Holders', 'Insiders vs Non-Insiders'),
    )

    if option == 'All Holders':

        fig = px.area(ape_holders)
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Token Supply',
            legend_title='Holders',
            plot_bgcolor='rgba(0, 0, 0, 0)',
        )

        st.plotly_chart(fig, use_container_width=True)

    elif option == 'Insiders vs Non-Insiders':

        fig = px.area(ape[['Insiders', 'Non-Insiders']])
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Token Supply',
            legend_title='Holders',
            plot_bgcolor='rgba(0, 0, 0, 0)',
        )

        st.plotly_chart(fig, use_container_width=True)


if __name__ == '__main__':
    st.set_page_config(page_title='Apecoin Supply Distribution Tracker')
    main()
