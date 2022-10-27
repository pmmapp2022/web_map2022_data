
from datetime import datetime
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print(f"Start {current_time}\n")





# KEY variables:
root_path = '/home/ubuntu/Pmm_web_map/'

geojson_path= root_path + 'geojson_test.json.geojson'
service_account_file_path = root_path + 'Sheets_key.json'
df_new_path = root_path + 'sheets_to_csv_test.csv'
df_old_path = root_path + 'Web_map_points.csv'

SPREADSHEET_ID = '1aZaBaZtzhkWO-wY2IiPEM6bR7q-i4O19NWUgPpcL7Qw'

PATH_OF_GIT_REPO = root_path + '.git'  # make sure .git folder is properly configured
COMMIT_MESSAGE = 'comment from python script'


# Tuturial followed https://www.youtube.com/watch?v=4ssigWmExak

import pandas as pd

from googleapiclient.discovery import build
from google.oauth2 import service_account

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = None

# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.

creds = service_account.Credentials.from_service_account_file(service_account_file_path, scopes=SCOPES)

service = build('sheets', 'v4', credentials=creds)

# Call the Sheets API
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                            range="Data_input!A2:I500").execute()
values = result.get('values', [])

# make dataframe from sheets values
df_sheets = pd.DataFrame(values[1:], columns = values[0])

df_sheets.to_csv(df_new_path, index=False)

print(df_sheets)


from geojson import Feature, FeatureCollection, Point
import json
import numpy as np

# CSV to Geojson function

from git import Repo


def git_push():

    repo = Repo(PATH_OF_GIT_REPO)
    print('1', repo)
    print(repo.git.status())

    repo.git.add(all=True)
    print('2')
    print(repo.git.status())

    repo.index.commit(COMMIT_MESSAGE)
    print('3')
    print(repo.git.status())

    origin = repo.remote(name='origin')
    print('4')
    assert origin.exists()
    print(repo.git.status())

    origin.push("master")

    print('5','pushed')
    print(repo.git.status())




def CSV_to_Geojson():

    print('CSV_to_Geojson() START')

    df_from_csv = pd.read_csv(df_old_path)

    def lat_func(row):
            try:
                lat = row['Coordinates'].split(',')[1]
                return lat
            except:
                print('WARNING: row missing coordinates')
                lat = np.nan
                return lat

    def lng_func(row):
            try:
                lng = row['Coordinates'].split(',')[0]
                return lng
            except:
                lng = np.nan
                print('WARNING: row missing coordinates')
                return lng

    df_from_csv['lat'] = df_from_csv.apply(lambda row: lng_func(row), axis=1)
    df_from_csv['lng'] = df_from_csv.apply(lambda row: lat_func(row), axis=1)

    df_from_csv['lat'] = df_from_csv['lat'].astype(float)
    df_from_csv['lng'] = df_from_csv['lng'].astype(float)


    # geometry filtering
    geometry = df_from_csv.apply(
        lambda row: Feature(geometry=Point((float(row['lng']), float(row['lat'])))),
        axis=1).tolist()

    # all the other columns used as properties
    properties = df_from_csv.drop(['lat', 'lng'], axis=1).to_dict('records')

    # make feature list
    features_list = []

    for i, x in zip(geometry, properties):
        i2 = i
        i2['properties'] = x
        features_list.append(i)

    #print('features_list first item:', features_list[0])

    # Export geojson as feature collection
    feature_collection = FeatureCollection(features_list)

    with open(geojson_path, 'w', encoding='utf-8') as f:
        json.dump(feature_collection, f, ensure_ascii=False)

    print('CSV_to_Geojson() FINISH')

print(df_new_path)


df_new = pd.read_csv(df_new_path, index_col='ID')

df_old = pd.read_csv(df_old_path, index_col='ID')


if df_old.equals(df_new):
    print('The same')

else:
    df_new.to_csv(df_old_path) # overwrite old csv with new
    CSV_to_Geojson() # overwrite old geojson with new
    print('NOT the same')


df_new2 = pd.read_csv(df_new_path, index_col='ID')

df_old2 = pd.read_csv(df_old_path, index_col='ID')


if df_old2.equals(df_new2):
    print('The same')


else:
    print('NOT the same')


git_push()

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print(f"End {current_time}\n")
