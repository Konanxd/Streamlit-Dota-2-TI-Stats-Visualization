import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import numpy as np

st.set_page_config(page_title="DOTA 2 The International Matches Tracker",
                   page_icon=":bar_chart:",
                   layout="wide")


@st.cache_data
def read_data():
    df = pd.read_parquet(
        'dota2_matches.parquet',
    )
    df = df[df['league'].str.contains('The International', regex=False)]
    return df


hero_id = pd.read_csv(
    'All_Heroes_ID.csv'
)

df = read_data()

# DATAFRAME DISPLAY CONFIG


def display(value):
    match_list = value[['match_id', 'league', 'match_start_date_time',
                        'radiant_team_name', 'dire_team_name']]

    config = {
        'match_id': st.column_config.NumberColumn(
            'Match ID',
            format='%d',
            step=1,
        ),
        'league': "League",
        'match_start_date_time': st.column_config.DatetimeColumn(
            "Date and Time",
            format="D MMM YYYY, h:mm a",
            step=60,
        ),
        'radiant_team_name': "Radiant Team",
        'dire_team_name': "Dire Team",
    }
    st.dataframe(
        match_list,
        column_config=config,
        use_container_width=True,
        hide_index=True
    )


# st.write(df)
# --SIDEBAR AND FILTER--
st.sidebar.header("Filter")
toggler_or_and = st.sidebar.toggle(label="And/Or Hero Filter")
if toggler_or_and:
    hero = st.sidebar.multiselect(
        "Or",
        options=hero_id['Name'].unique(),
        default=None
    )
else:
    hero = st.sidebar.multiselect(
        "And",
        options=hero_id['Name'].unique(),
        default=None
    )
player = st.sidebar.text_input(
    "Player's Nickname",
)
team = st.sidebar.text_input(
    "Team",
)

# ---FILTERS LOGIC---
player_counter = [
    f'radiant_player_{i}' for i in range(1, 6)
] + [
    f'dire_player_{i}' for i in range(1, 6)
]


def check_heroes(row):
    founded = sum([(pd.notna(row[col]) and row[col] in hero)
                   for col in [f'{pc}_hero' for pc in player_counter]])
    return founded >= 2


def display_filter():
    df_selection = df
    query_conditions = ''

    conditions = []

    if hero:
        # Construct hero conditions
        hero_conditions = ' | '.join(
            [f'{col}_hero == @hero' for col in player_counter])
        conditions.append(f'({hero_conditions})')

    if player:
        # Construct player conditions
        player_conditions = ' | '.join(
            [f'{col}_name in @player' for col in player_counter])
        conditions.append(f'({player_conditions})')

    if team:
        # Construct team conditions
        team_conditions = '@team == radiant_team_name | @team == dire_team_name'
        conditions.append(f'({team_conditions})')

    # Check if any conditions were generated
    if conditions:
        # Combine conditions using OR logic when the toggle is set to 'Or'
        if toggler_or_and:
            query_conditions = ' | '.join(conditions)
        # Combine conditions using AND logic when the toggle is set to 'And'
        else:
            query_conditions = ' & '.join(conditions)
    else:
        display(df)
    df_selection = df.query(query_conditions)

    if df_selection.empty:
        display(df)
    elif hero and toggler_or_and:
        display(df_selection)
    elif hero and not toggler_or_and:
        df_filtered = df_selection[df_selection.apply(check_heroes, axis=1)]
        display(df_filtered)
    else:
        display(df_selection)


# --DISPLAY DETAILS--

input = st.text_input("Input the match ID to display details")


def show_details(value):
    df_details = df.query(f'match_id == {value}')
    if not df_details.empty:
        radiant_score = df_details.iloc[0]['radiant_kills']
        dire_score = df_details.iloc[0]['dire_kills']

        radiant_win = df_details.iloc[0]['radiant_team_id']
        dire_win = df_details.iloc[0]['dire_team_id']
        winner = df_details.iloc[0]['winner_id']

        radiant, kills_disp, dire = st.columns([2, 1, 2], gap="medium")

        with radiant:
            radiant_team = df_details.iloc[0]['radiant_team_name']
            if winner == radiant_win:
                st.markdown(f"""
                            <table style="border: none;width:100%">
                            <tr style="border: none;">
                            <th colspan=6 style="border: none;"><h1 style="text-align: left;color: green">Radiant WIN</h1></th>
                            </tr>
                            <tr style="border: none;">
                            <th colspan=6 style="border: none;"><h4 style="text-align: left;">{radiant_team}</h4></th>
                            </tr>
                            """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                            <table style="border: none;width:100%">
                            <tr style="border: none;">
                            <th colspan=6 style="border: none;"><h1 style="text-align: left;color: green">Radiant</h1></th>
                            </tr>
                            <tr style="border: none;">
                            <th colspan=6 style="border: none;"><h4 style="text-align: left;">{radiant_team}</h4></th>
                            </tr>
                            """, unsafe_allow_html=True)
            for i in range(1, 6):
                radiant_player_name = df_details.iloc[0][f'radiant_player_{i}_name']
                radiant_player_pick = df_details.iloc[0][f'radiant_player_{i}_hero']
                radiant_player_position = df_details.iloc[0][f'radiant_player_{i}_position']
                radiant_player_kills = df_details.iloc[0][f'radiant_player_{i}_kills']
                radiant_player_deaths = df_details.iloc[0][f'radiant_player_{i}_deaths']
                radiant_player_assists = df_details.iloc[0][f'radiant_player_{i}_assists']
                radiant_player_networth = df_details.iloc[0][f'radiant_player_{i}_networth']

                if radiant_player_position == "POSITION_1":
                    radiant_player_position = "Carry"
                elif radiant_player_position == "POSITION_2":
                    radiant_player_position = "Mid"
                elif radiant_player_position == "POSITION_3":
                    radiant_player_position = "Offlane"
                elif radiant_player_position == "POSITION_4":
                    radiant_player_position = "Soft Support"
                elif radiant_player_position == "POSITION_5":
                    radiant_player_position = "Hard Support"

                st.markdown(f"""
                            <style>
                            table:{{ 
                                width:100%;
                             }}
                            .col1 {{ 
                                width:40%
                             }}
                            .col2 {{ 
                                width:25%
                             }}
                            .col3 {{ 
                                width:5%
                             }}
                            .col4 {{ 
                                width:5%
                             }}
                            .col5 {{ 
                                width:5%
                             }}
                            .col6 {{ 
                                width:20%
                             }}
                            </style>
                            <table style="border: none;width:100%">            
                            <tr style="border: none;">
                            <th colspan=6 style="border: none;"><h4 style="text-align: left;">{radiant_player_name}</h4></th>
                            </tr>
                            <tr style="border: none;">
                            <th class=col1 style="border: none;">Pick</td>
                            <th class=col2 style="border: none;">Position</td>
                            <th class=col3 style="border: none;">K</td>
                            <th class=col4 style="border: none;">D</td>
                            <th class=col5 style="border: none;">A</td>
                            <th class=col6 style="border: none;">Networth</td>
                            </tr>
                            <tr style="border: none;">
                            <td style="border: none;">{radiant_player_pick}</td>
                            <td style="border: none;">{radiant_player_position}</td>
                            <td style="border: none;">{radiant_player_kills}</td>
                            <td style="border: none;">{radiant_player_deaths}</td>
                            <td style="border: none;">{radiant_player_assists}</td>
                            <td style="border: none;color: gold;">{radiant_player_networth}</td>
                            </tr>
                            </table>
                            """, unsafe_allow_html=True)

        with kills_disp:
            duration_seconds = df_details.iloc[0]['match_duration_seconds']
            seconds = int(duration_seconds)
            duration_time = f"{seconds // 60:02d}:{seconds % 60:02d}"
            st.markdown(
                f'<h1 style="text-align: center";><span style="color: green">{radiant_score}</span> - <span style="color: red">{dire_score}</span></h1><h2 style="text-align: center">Duration</h2><h2 style="text-align: center">{duration_time}</h2>', unsafe_allow_html=True)

        with dire:
            # DIRE TEAM
            dire_team = df_details.iloc[0]['dire_team_name']
            if winner == dire_win:
                st.markdown(f"""
                                <table style="border: none;width:100%">
                                <tr style="border: none;">
                                <th colspan=6 style="border: none;"><h1 style="text-align: right;color: red">WIN Dire</h1></th>
                                </tr>
                                <tr style="border: none;">
                                <th colspan=6 style="border: none;"><h4 style="text-align: right;">{dire_team}</h4></th>
                                </tr>
                                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                                <table style="border: none;width:100%">
                                <tr style="border: none;">
                                <th colspan=6 style="border: none;"><h1 style="text-align: right;color: red">Dire</h1></th>
                                </tr>
                                <tr style="border: none;">
                                <th colspan=6 style="border: none;"><h4 style="text-align: right;">{dire_team}</h4></th>
                                </tr>
                                """, unsafe_allow_html=True)
            for i in range(1, 6):
                dire_player_name = df_details.iloc[0][f'dire_player_{i}_name']
                dire_player_pick = df_details.iloc[0][f'dire_player_{i}_hero']
                dire_player_position = df_details.iloc[0][f'dire_player_{i}_position']
                dire_player_kills = df_details.iloc[0][f'dire_player_{i}_kills']
                dire_player_deaths = df_details.iloc[0][f'dire_player_{i}_deaths']
                dire_player_assists = df_details.iloc[0][f'dire_player_{i}_assists']
                dire_player_networth = df_details.iloc[0][f'dire_player_{i}_networth']

                if dire_player_position == "POSITION_1":
                    dire_player_position = "Carry"
                elif dire_player_position == "POSITION_2":
                    dire_player_position = "Mid"
                elif dire_player_position == "POSITION_3":
                    dire_player_position = "Offlane"
                elif dire_player_position == "POSITION_4":
                    dire_player_position = "Soft Support"
                elif dire_player_position == "POSITION_5":
                    dire_player_position = "Hard Support"

                st.markdown(f"""
                            <style>
                            table:{{ 
                                width:100%;
                             }}
                            .col1 {{ 
                                width:40%
                             }}
                            .col2 {{ 
                                width:25%
                             }}
                            .col3 {{ 
                                width:5%
                             }}
                            .col4 {{ 
                                width:5%
                             }}
                            .col5 {{ 
                                width:5%
                             }}
                            .col6 {{ 
                                width:20%
                             }}
                            </style>
                            <table style="border: none;width:100%">            
                            <tr style="border: none;">
                            <th colspan=6 style="border: none;"><h4 style="text-align: right;">{dire_player_name}</h4></th>
                            </tr>
                            <tr style="border: none;">
                            <th class=col1 style="border: none;">Pick</td>
                            <th class=col2 style="border: none;">Position</td>
                            <th class=col3 style="border: none;">K</td>
                            <th class=col4 style="border: none;">D</td>
                            <th class=col5 style="border: none;">A</td>
                            <th class=col6 style="border: none;">Networth</td>
                            </tr>
                            <tr style="border: none;">
                            <td style="border: none;">{dire_player_pick}</td>
                            <td style="border: none;">{dire_player_position}</td>
                            <td style="border: none;">{dire_player_kills}</td>
                            <td style="border: none;">{dire_player_deaths}</td>
                            <td style="border: none;">{dire_player_assists}</td>
                            <td style="border: none;color: gold;">{dire_player_networth}</td>
                            </tr>
                            </table>
                            """, unsafe_allow_html=True)

        # PLOT
        # NETWORTH GRAPH
        button_networth = st.button("Networth")
        button_kda = st.button("KDA Ratio")

        if button_networth:
            radiant_networth = [
                df_details[f'radiant_player_{i}_networth'] for i in range(1, 6)]
            radiant_name = [
                df_details[f'radiant_player_{i}_name'] for i in range(1, 6)]
            radiant_networth = [
                item for sublist in radiant_networth for item in sublist]
            radiant_name = [
                item for sublist in radiant_name for item in sublist]
            dire_networth = [
                df_details[f'dire_player_{i}_networth'] for i in range(1, 6)]
            dire_name = [
                df_details[f'dire_player_{i}_name'] for i in range(1, 6)]
            dire_networth = [
                item for sublist in dire_networth for item in sublist]
            dire_name = [
                item for sublist in dire_name for item in sublist]
            # radiant_name.reverse()
            # dire_name.reverse()
            radiant_df = pd.DataFrame(
                {'name': radiant_name, 'networth': radiant_networth})
            dire_df = pd.DataFrame(
                {'name': dire_name, 'networth': dire_networth})
            radiant_df['color'] = 'green'
            dire_df['color'] = 'red'
            merged_df = pd.concat([radiant_df, dire_df])
            merged_df = merged_df.iloc[::-1]
            fig_networth_team = go.Figure(go.Bar(
                x=merged_df['networth'],
                y=merged_df['name'],
                orientation="h",  # Horizontal orientation
                marker=dict(color=merged_df['color'])
            ))
            fig_networth_team.update_layout(
                title="Player Net Worth",
                xaxis_title="Net Worth",
                yaxis_title="Player",
            )
            st.plotly_chart(fig_networth_team)

        if button_kda:
            radiant_name = [
                df_details[f'radiant_player_{i}_name'] for i in range(1, 6)]
            radiant_kills = np.array([
                df_details[f'radiant_player_{i}_kills'] for i in range(1, 6)])
            radiant_assists = np.array([
                df_details[f'radiant_player_{i}_assists'] for i in range(1, 6)])
            radiant_deaths = np.array([
                df_details[f'radiant_player_{i}_deaths'] for i in range(1, 6)])
            radiant_name = [
                item for sublist in radiant_name for item in sublist]
            radiant_kills = np.array([
                item for sublist in radiant_kills for item in sublist])
            radiant_assists = np.array([
                item for sublist in radiant_assists for item in sublist])
            radiant_deaths = np.array([
                item for sublist in radiant_deaths for item in sublist])
            radiant_formula = np.array([
                (radiant_kills + radiant_assists) / radiant_deaths])
            radiant_ratio = np.array([
                item for sublist in radiant_formula for item in sublist])
            dire_name = [
                df_details[f'dire_player_{i}_name'] for i in range(1, 6)]
            dire_kills = np.array([
                df_details[f'dire_player_{i}_kills'] for i in range(1, 6)])
            dire_assists = np.array([
                df_details[f'dire_player_{i}_assists'] for i in range(1, 6)])
            dire_deaths = np.array([
                df_details[f'dire_player_{i}_deaths'] for i in range(1, 6)])
            dire_name = np.array([
                item for sublist in dire_name for item in sublist])
            dire_kills = np.array([
                item for sublist in dire_kills for item in sublist])
            dire_assists = np.array([
                item for sublist in dire_assists for item in sublist])
            dire_deaths = np.array([
                item for sublist in dire_deaths for item in sublist])
            dire_formula = np.array([
                (dire_kills + dire_assists) / dire_deaths])
            dire_ratio = np.array([
                item for sublist in dire_formula for item in sublist])
            radiant_df = pd.DataFrame(
                {'name': radiant_name, 'ratio': radiant_ratio})
            dire_df = pd.DataFrame(
                {'name': dire_name, 'ratio': dire_ratio})
            radiant_df['color'] = 'green'
            dire_df['color'] = 'red'
            merged_df = pd.concat([radiant_df, dire_df])
            merged_df = merged_df.iloc[::-1]
            fig_ratio_team = go.Figure(go.Bar(
                x=merged_df['ratio'],
                y=merged_df['name'],
                orientation="h",  # Horizontal orientation
                marker=dict(color=merged_df['color'])
            ))
            fig_ratio_team.update_layout(
                title="Player Net Worth",
                xaxis_title="Net Worth",
                yaxis_title="Player",
            )
            st.plotly_chart(fig_ratio_team)

    else:
        st.write("No match found for the provided match ID")


# --OUTPUT--

find_button = st.sidebar.button("Find")


def to_display():
    if find_button:
        value = display_filter()
    else:
        value = display(df)
    return value


to_display()


if input:
    show_details(input)
