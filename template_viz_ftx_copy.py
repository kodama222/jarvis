import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

coins = ['fida', 'oxy', 'maps']

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


def inflation(df, dict):
    
    d = int(''.join(filter(str.isdigit, dict['emission_schedule'])))

    s0 = df.total[0]
    t0 = df.index[0]
    l = [0]
    j = 0

    for i in range(1, len(df)):
        if (df.index[i] - t0) < pd.Timedelta(days=365):
            l.append((df.total[i] - s0) / s0 * d / i)
            j += 1
        else:
            l.append(
                (df.total[i] - df.total[i - j])
                / df.total[i - j]
            )
    return np.array(l) * 100


@st.cache(suppress_st_warning=True)
def read_data():

    urls = [
        f'https://raw.githubusercontent.com/kodama222/jarvis/main/data/ftx/{coin}.csv'
        for coin in coins
    ]

    data_dict = {}
    dist_dict = {}
    supply_dict = {}
    totalsupply_dict = {}
    parties_dict = {}

    for u in urls:

        # take file name
        f0 = os.path.basename(u)
        f1 = f0.rsplit('.')[0].upper()

        ## READ DATA
        # general token data
        df_data = pd.read_csv(u, skiprows=[0], nrows=7).set_index('key')
        dict_data = df_data['data'].to_dict()

        # data related to token distribution among different parties
        df_distribution = pd.read_csv(u, skiprows=np.linspace(0, 9, 10))

        # supply for entities based on data from above
        supply = df_distribution.iloc[5:]
        dates = pd.date_range(
            start=dict_data['start_date'],
            periods=len(supply),
            freq=dict_data['emission_schedule'],
        )  # calculate datetime
        supply = supply.set_index(dates).drop(
            columns='entity'
        )  # set index as date
        supply = supply.astype(float)

        # substract burn from company treasury
        for k in supply.keys():
            if k == 'burn':
                try:
                    supply.treasury = supply.treasury - supply.burn
                except:
                    pass
                try:
                    supply.company = supply.company - supply.burn
                except:
                    pass

        # classify entities
        df_distribution = df_distribution.drop(columns='entity')

        team = df_distribution.iloc[3] == 'team_advisors'
        investors = df_distribution.iloc[3] == 'investor'
        public = df_distribution.iloc[3] == 'public'
        foundation = df_distribution.iloc[3] == 'foundation'
        validators = df_distribution.iloc[3] == 'validators'
        ecosystem = df_distribution.iloc[3] == 'ecosystem'
        
        parties = [team, investors, public, foundation, validators, ecosystem]

        team_df = supply[supply.columns[team.values]]
        investors_df = supply[supply.columns[investors.values]]
        public_df = supply[supply.columns[public.values]]
        foundation_df = supply[supply.columns[foundation.values]]
        ecosystem_df = supply[supply.columns[ecosystem.values]]
        validators_df = supply[supply.columns[validators.values]]

        # total supply
        totalsupply = pd.concat(
            [
                supply,
                team_df.sum(axis=1),
                investors_df.sum(axis=1),
                public_df.sum(axis=1),
                foundation_df.sum(axis=1),
                ecosystem_df.sum(axis=1),
                validators_df.sum(axis=1),
            ],
            axis=1,
        )
        totalsupply = totalsupply.rename(
            columns={
                0: 'team_advisors',
                1: 'investors',
                2: 'public',
                3: 'foundation',
                4: 'ecosystem',
                5: 'validators',
            }
        )

        totalsupply['total'] = totalsupply[
            [
                'team_advisors',
                'investors',
                'public',
                'foundation',
                'ecosystem',
                'validators',
            ]
        ].sum(axis=1)
        totalsupply['new_supply'] = totalsupply.total.pct_change()

        totalsupply['annual_inflation'] = inflation(totalsupply, dict_data)

        # create dict entry with dataframe as value and filename as key
        data_dict[f1] = df_data
        dist_dict[f1] = df_distribution
        supply_dict[f1] = supply
        totalsupply_dict[f1] = totalsupply
        parties_dict[f1] = parties

    return data_dict, dist_dict, supply_dict, totalsupply_dict, parties_dict


def main():

    data_dict, dist_dict, supply_dict, totalsupply_dict, parties_dict = read_data()

    st.markdown(
        """
    # **Token Supply Distribution**
    """
    )

    token = st.sidebar.selectbox(
        'What token do you want to know more about?',
        [coin.upper() for coin in coins],
    )

    all_initial_allo = (
        dist_dict[token]
        .iloc[3]
    ).astype(float)
    
    parties_initial_allo = [all_initial_allo[all_initial_allo.index[p.values]].sum() for p in parties_dict[token]]

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
                    'team_advisors',
                    'investors',
                    'public',
                    'foundation',
                    'ecosystem',
                    'validators',
                    'annual_inflation',
                    'total',
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
                    'team_advisors',
                    'investors',
                    'public',
                    'foundation',
                    'ecosystem',
                    'validators',
                    'annual_inflation',
                    'total',
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
                    labels=[
                        'Team & Advisors',
                        'Investors',
                        'Public',
                        'Foundation',
                        'Ecosystem',
                        'Validators'
                    ],
                    values=parties_initial_allo,
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
            totalsupply_dict[token][
                [
                    'team_advisors',
                    'investors',
                    'public',
                    'foundation',
                    'ecosystem',
                    'validators'
                ]
            ]
        )
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Token Supply',
            legend_title='Holders',
            plot_bgcolor='rgba(0, 0, 0, 0)',
        )
        newnames = {
                'team_advisors':'Team & Advisors',
                'investors':'Investors',
                'public':'Public',
                'foundation':'Foundation',
                'ecosystem':'Ecosystem',
                'validators':'Validators'
        }
        fig.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                            legendgroup = newnames[t.name],
                                            hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])
                                            )
                        )

        st.plotly_chart(fig, use_container_width=True)

        # Evolution of supply distribution %
        fig = px.area(
            totalsupply_dict[token][
                [
                    'team_advisors',
                    'investors',
                    'public',
                    'foundation',
                    'ecosystem',
                    'validators',
                ]
            ],
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
        newnames = {
                'team_advisors':'Team & Advisors',
                'investors':'Investors',
                'public':'Public',
                'foundation':'Foundation',
                'ecosystem':'Ecosystem',
                'validators':'Validators'
        }
        fig.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                            legendgroup = newnames[t.name],
                                            hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])
                                            )
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
