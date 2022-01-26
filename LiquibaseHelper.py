from glob import glob
import re 
import pathlib
import fileinput
import sys
from numpy import real
import pandas as pd

version = 'v1.4.0'

def changeset_parser(line: str) -> dict:
    """ parses a given changeset into a dictionary format"""
    lineparts = line.split()
    changeset_dict = {}
    options = ['runWith', 'runAlways', 'runOnChange', 'labels', 'contexts']
    for part in lineparts:
        #print(lineparts)
        if 'sql-' in part:
            changeset_dict['id'] = part
        for option in options:
            if option in part:
                changeset_dict[option] = part.replace(f'{option}:','')
                options.remove(option)
        # assign remaining blank values
        for option in options:
            if option in ['labels','contexts']:
                changeset_dict[option] = ''
            else:
                changeset_dict[option] = 'false'
    if changeset_dict['id'] == '':
        raise Exception('NO ID FOUND FOR CHANGESET: '+ line)
    return changeset_dict

def increment_changeset(file):
    n = 1
    for line in fileinput.input(file, inplace=1):
        #print(line)
        if '--changeset' in line:
            if '.sql' in line:
                line = line.replace('.sql-x', f'.sql-{n}')
                line = line.replace('.sql ', f'.sql-{n} ')
                n+=1
        sys.stdout.write(line)

def export_changesets_to_csv(changeset_dict: dict, filename: str):
    df = pd.DataFrame(changeset_dict)
    df.to_csv(filename, index=False)

def version_and_increment_reset(version, sql_file):
    chng_log = pathlib.Path(sql_file)
    #print(sql_file)
    text = chng_log.read_text()
    # reset - replace current numbers with x
    repl_num_text = re.sub(
        '.sql-\d+',
        '.sql-x',
        text
    )
    # update version
    repl_v_text = re.sub(
        'v(-)?\d+\.\d+\.\d+',
        version,
        repl_num_text
    )
    chng_log.write_text(repl_v_text)

sql_files = glob(f'./{version}/*.sql')

# do initial reset of changeset id numbers and set version
for sql_file in sql_files:
    version_and_increment_reset(version, sql_file)
    increment_changeset(sql_file)

# comb through and retrieve all changesets - export to csv
existing_changesets = []
for sql_file in sql_files:
    with open(sql_file, 'r') as read_sql_file:
        lines = read_sql_file.readlines()
        for line in lines:
            if '--changeset' in line:
                existing_changesets.append(changeset_parser(line))

#print(existing_changesets)

export_changesets_to_csv(existing_changesets, 'export.csv')

