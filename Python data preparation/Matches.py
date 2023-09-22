import pandas as pd
import numpy as np
from kaggle.api.kaggle_api_extended import KaggleApi
from zipfile import ZipFile
from sqlalchemy import create_engine

#downloading dataset from kaggle
api = KaggleApi()
api.authenticate()

api.dataset_download_files('afnanurrahim/premier-league-2022-23')


#extracting csv files from zip file
zf = ZipFile('premier-league-2022-23.zip')
zf.extractall()
zf.close()

match_results = pd.read_csv('2023_matchday_results.csv')
match_results['fixture.date'] = pd.to_datetime(match_results['fixture.date'])
match_results['match_date'] = match_results['fixture.date'].dt.date
match_results['match_time'] = match_results['fixture.date'].dt.time

home_team_stats = pd.read_csv('2023_home_teams_stats.csv')
away_team_stats = pd.read_csv('2023_away_teams_stats.csv')
standings = pd.read_csv('2023_PL_standings.csv')


#dropping unwanted columns
match_results.drop(['Unnamed: 0','teams.away.winner','fixture.date','teams.home.winner'], axis=1, inplace=True)

home_team_stats.drop(['Shots off Goal',  'Blocked Shots', 'Shots insidebox','Shots outsidebox','Goalkeeper Saves','Total passes', 'Passes accurate', 'Passes %'],
                     axis=1, inplace=True)

away_team_stats.drop(['Shots off Goal', 'Blocked Shots', 'Shots insidebox','Shots outsidebox','Goalkeeper Saves','Total passes', 'Passes accurate', 'Passes %'],
                     axis=1, inplace=True)


#merging home and away team stats into one df
home_team_stats.rename(columns={'Home team id':'team_id', 'Home team name':'team_name'}, inplace=True)
home_team_stats['is_home'] = 1

away_team_stats.rename(columns={'away team id':'team_id', 'away team name':'team_name'}, inplace=True)
away_team_stats['is_home'] = 0

team_stats = pd.concat([home_team_stats, away_team_stats])

team_stats[['Shots on Goal', 'Total Shots','Fouls', 'Corner Kicks', 'Offsides','Yellow Cards','Red Cards']] = \
    team_stats[['Shots on Goal', 'Total Shots','Fouls', 'Corner Kicks', 'Offsides','Yellow Cards','Red Cards']].fillna(0)


#adding matchday_number column to results and stats table
match_results.sort_values(by=['match_date','match_time'], ascending=True, inplace=True)
match_results['matchday_number'] = [(i // 10) + 1 for i in range(match_results.shape[0])]

#adding referee_id foreign key to the data, the data about which referee officiated which matches is made-up
referees_id = pd.read_csv('../data/main/referees.csv', usecols=[0])

num_rows = match_results.shape[0]

referee = np.random.choice(referees_id['referee_id'].to_list(), size=num_rows)
match_results['referee_id'] = referee

print(match_results['referee_id'].value_counts())


team_stats.rename(columns={'fixture id':'fixture.id'}, inplace=True)
team_stats = team_stats.merge(match_results[['fixture.id', 'matchday_number']], how='left', on='fixture.id')


"""spliting the data into 2 parts, the first part will be loaded directly while creating the database, 
   and the second part will be merged into database later through SSIS"""
team_stats[['team_id','Shots on Goal','Total Shots','Fouls','Corner Kicks','Offsides','Yellow Cards','Red Cards']] = \
    team_stats[['team_id','Shots on Goal','Total Shots','Fouls','Corner Kicks','Offsides','Yellow Cards','Red Cards']].astype(int)

match_results_main = match_results[match_results['matchday_number'] < 30]
match_results_additional = match_results[match_results['matchday_number'] >= 30]

team_stats_main = team_stats[team_stats['matchday_number'] < 30]
team_stats_additional = team_stats[team_stats['matchday_number'] >= 30]



#Saving the files
match_results_main.to_csv('../data/main/match_results.csv',index=False)
match_results_additional.to_csv('../data/additional/match_results.csv',index=False)

team_stats_main.to_csv('../data/main/team_stats.csv',index=False)
team_stats_additional.to_csv('../data/additional/team_stats.csv',index=False)

Matches = match_results_main[['fixture.id','match_date','match_time', 'teams.home.id', 'teams.away.id', 'goals.home', 'goals.away', 'referee_id', 'matchday_number']]
Matches = Matches.rename(columns={'fixture.id':'match_id', 'teams.home.id':'home_team_id', 'teams.away.id':'away_team_id', 'goals.home':'home_team_goals', 'goals.away':'away_team_goals'})

TeamMatchStats = team_stats_main[['fixture.id', 'team_id', 'is_home', 'Shots on Goal', 'Total Shots', 'Fouls', 'Corner Kicks', 'Ball Possession', 'Yellow Cards',
                                  'Red Cards', 'expected_goals']]
TeamMatchStats = TeamMatchStats.rename(columns = {'fixture.id':'match_id','team_id':'club_id', 'Shots on Goal':'shots_on_goal', 'Total Shots': 'total_shots', 'Fouls':'fouls', \
                                'Corner Kicks':'corner_kicks', 'Ball Possession':'ball_possession', 'Yellow Cards': 'yellow_cards','Red Cards': 'red_cards' })

TeamMatchStats['ball_possession'] = TeamMatchStats['ball_possession'].str[:-1].astype('Int64')

#saving data into database
server = 'DESKTOP-123'
database = 'Premier League 22/23'
trusted_connection = 'yes'
driver = 'ODBC Driver 17 for SQL Server'

conn_str = f'mssql+pyodbc://{server}/{database}?trusted_connection={trusted_connection}&driver={driver}'
engine = create_engine(conn_str)


Matches.to_sql(name="Matches", con=engine, if_exists="append", index=False)
TeamMatchStats.to_sql(name="TeamMatchStats", con=engine, if_exists="append", index=False)