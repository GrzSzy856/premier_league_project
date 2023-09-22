import pandas as pd
import random
from sqlalchemy import create_engine

club_ids = pd.read_csv('../data/main/club_id_dict.csv')
managers = pd.read_excel('../data/managers_raw.xlsx')
referees = pd.read_excel('../data/referees_raw.xlsx')
stadiums = pd.read_excel('../data/stadiums_raw.xlsx')

#generating primary keys
def generate_artificial_key(x, y):
    keys = list(range(x, y))
    random.shuffle(keys)
    return keys

managers['manager_id'] = generate_artificial_key(0, managers.shape[0])
referees['referee_id'] = generate_artificial_key(0, referees.shape[0])
stadiums['stadium_id'] = generate_artificial_key(0, stadiums.shape[0])



clubs = club_ids.merge(managers[['Club', 'manager_id']], how='left', left_on='club_name', right_on='Club').merge(stadiums[['Club', 'stadium_id']], how='left', left_on='club_name', right_on='Club')
clubs.drop(['Club_x', 'Club_y'], axis=1, inplace=True)
clubs = clubs[['club_id','stadium_id','manager_id','club_name','name_abbreviation']]
clubs['stadium_id'] = clubs['stadium_id'].astype('Int64')
clubs['manager_id'] = clubs['manager_id'].astype('Int64')

stadiums = stadiums[['stadium_id', 'stadium_name', 'City', 'Capacity']].rename(columns={'City':'city', 'Capacity':'capacity'})

managers[['manager_name', 'manager_surname']] = managers['Manager'].str.split(' ', n=1, expand=True)
managers.drop(['Manager'], axis=1, inplace=True)
managers = managers[['manager_id', 'manager_name', 'manager_surname', 'Nation', 'Date of birth', 'From']].rename(columns={'Nation':'nationality', 'Date of birth':'birth_date', 'From':'appointment_date'})


referees[['referee_name', 'referee_surname']] = referees['Name'].str.split(' ', n=1, expand=True)
referees.drop(['Name'], axis=1, inplace=True)


clubs.to_csv('../data/main/clubs.csv',index=False)
managers.to_excel('../data/main/managers.xlsx',index=False)
referees.to_csv('../data/main/referees.csv',index=False)
stadiums.to_csv('../data/main/stadiums.csv',index=False)


#saving data into database
server = 'DESKTOP-9BB8IGK'
database = 'Premier League 22/23'
trusted_connection = 'yes'
driver = 'ODBC Driver 17 for SQL Server'

conn_str = f'mssql+pyodbc://{server}/{database}?trusted_connection={trusted_connection}&driver={driver}'
engine = create_engine(conn_str)

managers.to_sql(name="Managers", con=engine, if_exists="append", index=False)

referees.to_sql(name="Referees", con=engine, if_exists="append", index=False)

stadiums.to_sql(name="Stadiums", con=engine, if_exists="append", index=False)
