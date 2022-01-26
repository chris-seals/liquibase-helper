from glob import glob
import re
import pathlib
import fileinput
import sys
from numpy import real
import pandas as pd


def recover_changesets_from_csv(filename: str):
    """turn csv file back into python dictionary for easy retrieval"""
    df = pd.read_csv(filename)
    booleanDictionary = {True: 'true', False: 'false'}
    df = df.replace(booleanDictionary).to_dict(orient='records')
    return df

def minesweeper(line:str, updated_changesets:dict):
    """ checks for missing id structure needed (sql file ending in ...sql-increment# """
    if 'sql-' not in line:
        raise Exception(f'MISSING SQL INCREMENT IN CHANGESET: {line}')
    try:
        id = [match for match in line.split() if 'sql-' in match][0]
        cd = list(
            filter(lambda changeset: changeset['id'] == id, updated_changesets))[0]
    except: 
        raise Exception('No matching ID for ' + line)

def remake_changeset(line:str, updated_changesets:list) -> str:
    """ swap out old changeset values for new """
    #print(line)
    id = [match for match in line.split() if 'sql-' in match][0]
    cd = list(
        filter(lambda changeset: changeset['id'] == id, updated_changesets))[0]

    line = f"--changeset {cd['id']} runWith:{cd['runWith']} labels:{cd['labels']} contexts:{cd['contexts']} runAlways:{cd['runAlways']} runOnChange:{cd['runOnChange']}\n"
    for item in ['runOnChange', 'runAlways']:
        if cd[item] == 'false':
            line = line.replace(f'{item}:false', '')
    return line 

version = 'v1.4.0'

sql_files = glob(f'./{version}/*.sql')

updated_changesets = recover_changesets_from_csv('export.csv')

def update_changesets(file):
    for line in fileinput.input(file, inplace=1):
        #print(line)
        if '--changeset' in line:
            minesweeper(line, updated_changesets)
            line = remake_changeset(line, updated_changesets)
        
        sys.stdout.write(line)

#print(updated_changesets)
#idoi = 'jace-plute:00301_pkg_sp_gpm_proc_map_gmted_data.sql-1'
#test_cs = '--changeset blah blah.sql-1 blah blah'

# print(list(filter(lambda changeset: changeset['id'] == idoi, updated_changesets))[0])

#print([match for match in test_cs.split() if 'sql-' in match])
#cd = list(
#     filter(lambda changeset: changeset['id'] == idoi, updated_changesets))[0]
# line = f"--changeset {cd['id']} runWith:{cd['runWith']} labels:{cd['labels']} contexts:{cd['contexts']} runAlways:{cd['runAlways'].lower()} runOnChange:{cd['runOnChange'].lower()}"
# for item in ['runOnChange', 'runAlways']:
#     if cd[item].lower() == 'false':
#         line = line.replace(f'{item}:false', '')

# print(line)

for file in sql_files:
   update_changesets(file)
