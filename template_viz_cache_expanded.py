from math import dist
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os


def distribution_type(x, df_distribution, df_data):
    if df_distribution[x.name][2] == 'percentage':
        return x
    elif df_distribution[x.name][2] == 'amount':
        return x / df_data.start_tokens[0] * 100


def burn(x, df_distribution, df_data):
    if df_distribution[x.name][4] == 'burn':
        return x
    else:
        return x


def inflation(df):

    s0 = df.total_monthly[0]
    t0 = df.index[0]
    l = [0]
    j = 0

    for i in range(1, len(df)):
        if (df.index[i] - t0) < pd.Timedelta(days=365):
            l.append((df.total_monthly[i] - s0) / s0 * 12 / i)
            j += 1
        else:
            l.append(
                (df.total_monthly[i] - df.total_monthly[i - j])
                / df.total_monthly[i - j]
            )
    return np.array(l) * 100


@st.cache
def read_data():

    capcoin_url = 'https://raw.githubusercontent.com/kodama222/jarvis/main/data/capcoin.csv'
    gmt_url = (
        'https://raw.githubusercontent.com/kodama222/jarvis/main/data/gmt.csv'
    )
    matic_url = 'https://raw.githubusercontent.com/kodama222/jarvis/main/data/matic.csv'
    monthcoin_url = 'https://raw.githubusercontent.com/kodama222/jarvis/main/data/monthcoin.csv'
    quartercoin_url = 'https://raw.githubusercontent.com/kodama222/jarvis/main/data/quartercoin.csv'

    urls = [capcoin_url, gmt_url, matic_url, monthcoin_url, quartercoin_url]

    data_dict = {}
    dist_dict = {}
    supply_dict = {}
    totalsupply_dict = {}

    for u in urls:

        # take file name
        f0 = os.path.basename(u)
        f1 = f0.rsplit('.')[0].upper()

        ## READ DATA
        # general data
        df_data = pd.read_csv(u, skiprows=[0], nrows=1)

        # distribution data
        df_distribution = pd.read_csv(u, skiprows=[0, 1, 2, 3])

        # supply for entities based on data from above
        supply = df_distribution.iloc[6:]
        dates = pd.date_range(
            start=df_data.start_date[0],
            periods=len(supply),
            freq=df_data.emission_schedule[0],
        )  # calculate datetime
        supply = supply.set_index(dates).drop(
            columns='entity'
        )  # set index as date
        supply = supply.astype(float)
        supply = supply.apply(
            lambda x: distribution_type(x, df_distribution, df_data)
        )

        for k in supply.keys():
            if k == 'burn':
                supply.treasury = supply.treasury - supply.burn

        # classify entities
        df_distribution = df_distribution.drop(columns='entity')
        team = df_distribution.iloc[3] == 'treasury'
        investors = df_distribution.iloc[3] == 'investor'
        public = df_distribution.iloc[3] == 'public'

        team_df = supply[supply.columns[team.values]]
        investors_df = supply[supply.columns[investors.values]]
        public_df = supply[supply.columns[public.values]]

        # total supply (including )
        totalsupply = pd.concat(
            [
                supply,
                team_df.sum(axis=1),
                investors_df.sum(axis=1),
                public_df.sum(axis=1),
            ],
            axis=1,
        )
        totalsupply = totalsupply.rename(
            columns={0: 'devs', 1: 'investors', 2: 'plebs'}
        )

        totalsupply['total_monthly'] = totalsupply[
            ['devs', 'investors', 'plebs']
        ].sum(axis=1)
        totalsupply['new_supply'] = totalsupply.total_monthly.pct_change()

        totalsupply['annual_inflation'] = inflation(totalsupply)

        # create dict entry with dataframe as value and filename as key
        data_dict[f1] = df_data
        dist_dict[f1] = df_distribution
        supply_dict[f1] = supply
        totalsupply_dict[f1] = totalsupply

    return data_dict, dist_dict, supply_dict, totalsupply_dict


def main():

    data_dict, dist_dict, supply_dict, totalsupply_dict = read_data()

    st.markdown(
        """
    # **Token Supply Distribution**
    """
    )

    token = st.sidebar.selectbox(
        'What token do you want to know more about?',
        ('GMT', 'CAPCOIN', 'QUARTERCOIN', 'MONTHCOIN', 'MATIC'),
    )

    all_initial_allo = (
        totalsupply_dict[token]
        .drop(
            columns=[
                'devs',
                'investors',
                'plebs',
                'annual_inflation',
                'total_monthly',
                'new_supply',
            ]
        )
        .iloc[-1]
    )
    parties_initial_allo = totalsupply_dict[token][
        ['devs', 'investors', 'plebs']
    ].iloc[-1]

    option = st.sidebar.selectbox(
        'What kinda chart do you want to see?',
        ('All Holders', 'Different Parties'),
    )

    if option == 'All Holders':

        # plotly pie chart of final token distribution
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=all_initial_allo.index,
                    values=all_initial_allo.values,
                )
            ]
        )
        fig.update_traces(
            textinfo='percent+label'
        )  # remove to show only % label on chart
        fig.update_layout(title_text=f'{token} Allocation', title_x=0.5)

        st.plotly_chart(fig, use_container_width=True)

        # stacked area chart of supply distribution
        fig = px.area(
            totalsupply_dict[token].drop(
                columns=[
                    'devs',
                    'investors',
                    'plebs',
                    'annual_inflation',
                    'total_monthly',
                    'new_supply',
                ]
            )
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
            totalsupply_dict[token].drop(
                columns=[
                    'devs',
                    'investors',
                    'plebs',
                    'annual_inflation',
                    'total_monthly',
                    'new_supply',
                ]
            ),
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

    elif option == 'Different Parties':

        # plotly pie chart of final token distribution
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=parties_initial_allo.index,
                    values=parties_initial_allo.values,
                )
            ]
        )
        fig.update_traces(
            textinfo='percent+label'
        )  # remove to show only % label on chart
        fig.update_layout(title_text=f'{token} Allocation', title_x=0.5)

        st.plotly_chart(fig, use_container_width=True)

        # stacked area chart of supply distribution
        fig = px.area(totalsupply_dict[token][['devs', 'investors', 'plebs']])
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Token Supply',
            legend_title='Holders',
            plot_bgcolor='rgba(0, 0, 0, 0)',
        )

        st.plotly_chart(fig, use_container_width=True)

        # Evolution of supply distribution %
        fig = px.area(
            totalsupply_dict[token][['devs', 'investors', 'plebs']],
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

    # combined
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=totalsupply_dict[token].index,
            y=totalsupply_dict[token]['new_supply'] * 100,
            name=f'{token} New Monthly Supply',
        )
    )
    fig.add_trace(
        go.Scatter(
            x=totalsupply_dict[token].index,
            y=totalsupply_dict[token]['annual_inflation'],
            name=f'{token} Annual Inflation',
            yaxis='y2',
        )
    )

    fig.update_xaxes(tickangle=45)
    fig.update_layout(
        yaxis=dict(
            title=f'{token} New Monthly Supply [%]',
            titlefont=dict(color='#1f77b4'),
            tickfont=dict(color='#1f77b4'),
            autotypenumbers='convert types',
            showgrid=True,
            gridcolor='rgba(166, 166, 166, 0.35)',
        ),
        yaxis2=dict(
            title=f'{token} Annual Inflation [%]',
            titlefont=dict(color='#d62728'),
            tickfont=dict(color='#d62728'),
            anchor='x',
            overlaying='y',
            side='right',
        ),
        showlegend=False,
        plot_bgcolor='white',
        autosize=False,
        width=800,
        height=550,
        title_x=0.5,
    )

    st.plotly_chart(fig, use_container_width=True)

    return


if __name__ == '__main__':
    st.set_page_config(page_title='Supply Distribution Tracker')
    main()
