import pandas as pd
import numpy as np
from kaggle.api.kaggle_api_extended import KaggleApi
from zipfile import ZipFile
from datetime import date
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine
import random

#downloading dataset from kaggle
api = KaggleApi()
api.authenticate()

api.dataset_download_files('lucas142129silva/fifa-23-ultimate-team-players-database')


#extracting csv files from zip file
zf = ZipFile('fifa-23-ultimate-team-players-database.zip')
zf.extractall()
zf.close()

player_stats = pd.read_csv('fifa23_players_2023-06-16.csv')

print(player_stats.columns)

print(player_stats.head(3))

print(player_stats[['Name', 'Club', 'Nation']].value_counts())
#There are many duplicates in the dataset, so i have to delete them

player_stats.drop_duplicates(subset=['Name', 'Club', 'Nation'], keep='last', inplace=True)

player_stats = player_stats[player_stats['League'] == 'Premier League']

player_stats = player_stats[['Name', 'Club', 'Nation', 'League', 'Rating', 'Main_Position',
                             'pace', 'shooting', 'passing', 'dribbling', 'defending', 'physicality', 'Height']]

player_stats['Height'] = player_stats['Height'].str[:3]

player_stats[['player_name', 'player_surname']] = player_stats['Name'].str.split(' ', n=1, expand=True)


def swap_names(row):
    if (pd.isna(row['player_surname'])) | (row['player_surname'] == ''):
        row['player_surname'], row['player_name'] = row['player_name'], ''
    return row

player_stats = player_stats.apply(swap_names, axis=1)


player_stats.drop(['Name'], axis=1, inplace=True)

#unfortunately i do not have necessary  better_foot, contract_expiration and birth_date columns so i will generate them "randomly" from certain range of values
num_rows = player_stats.shape[0]

probabilities_better_foot = [0.62, 0.3, 0.08]
better_foot = np.random.choice([ 'Right', 'Both', 'Left'], size=num_rows, p=probabilities_better_foot)
player_stats['better_foot'] = better_foot

print(player_stats['better_foot'].value_counts())

today = date.today()

contract_expiration_choice = [date.today() + relativedelta(years=1), date.today() + relativedelta(years=2), date.today() + relativedelta(years=3), date.today() + relativedelta(years=4)]
contract_expiration = np.random.choice(contract_expiration_choice, size=num_rows)
player_stats['contract_expiration'] = contract_expiration

print(player_stats['contract_expiration'].value_counts())

birth_date_choice = pd.date_range(start="1985-01-01",end="2002-01-01").to_list()
birth_date = np.random.choice(birth_date_choice, size=num_rows)
player_stats['birth_date'] = birth_date

print(player_stats['birth_date'].value_counts())

player_stats.rename(columns={'Club':'club_name'}, inplace=True)
clubs = pd.read_csv(r'C:\code\Projekt Baza PL\data\main\clubs.csv')
player_stats = player_stats.merge(clubs[['club_id', 'club_name']], how='left', on='club_name')
player_stats['club_id'] = player_stats['club_id'].astype('Int64')
player_stats = player_stats[pd.isna(player_stats['club_id']) == False]


def generate_artificial_key(x, y):
    keys = list(range(x, y))
    random.shuffle(keys)
    return keys

player_stats['player_id'] = generate_artificial_key(0, player_stats.shape[0])

player_values_path = r'C:\code\Projekt Baza PL\data\main\players_values.csv'
player_values = pd.read_csv(player_values_path)
player_stats = player_stats.merge(player_values[['player_name', 'player_surname', 'market_value_in_eur']], how='left', on=['player_name', 'player_surname'])

null_indices = player_stats[player_stats['market_value_in_eur'].isnull()].index
for idx in null_indices:
    random_value = np.random.uniform(1, 50)
    player_stats.at[idx, 'market_value_in_eur'] = round(random_value,1)

Players = player_stats[['player_id', 'club_id', 'player_name', 'player_surname', 'Nation', 'Main_Position', 'birth_date', 'contract_expiration', 'Height', 'better_foot','market_value_in_eur']]
Players = Players.rename(columns={'Nation':'nationality', 'Main_Position':'position', 'Height':'height', 'market_value_in_eur':'market_value_in_m_eur'})

PlayerAttributes =  player_stats[['player_id', 'pace', 'shooting', 'passing', 'dribbling', 'defending', 'physicality']]

player_stats.to_csv(r'C:\code\Projekt Baza PL\data\main\players_stats.csv', encoding='utf-8', index=False)

#saving data into database
server = 'DESKTOP-123'
database = 'Premier League 22/23'
trusted_connection = 'yes'
driver = 'ODBC Driver 17 for SQL Server'

conn_str = f'mssql+pyodbc://{server}/{database}?trusted_connection={trusted_connection}&driver={driver}'
engine = create_engine(conn_str)

Players.to_sql(name="Players", con=engine, if_exists="append", index=False)
PlayerAttributes.to_sql(name="PlayerAttributes", con=engine, if_exists="append", index=False)