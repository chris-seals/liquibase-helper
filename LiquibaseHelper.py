from glob import glob
import re 
import pathlib
import fileinput
import sys
from numpy import real
import pandas as pd
import os

version = 'v1.5.0'

# TODO make parser ensure the ID matches the filename
# TODO return a list of files that have no --liquibase formatted sql at the top
# TODO identify missing changesets

def changeset_parser(line: str) -> dict:
    """ parses a given changeset into a dictionary format"""
    lineparts = line.split()
    changeset_dict = {}
    options = ['runWith', 'runAlways', 'runOnChange', 'labels', 'context']
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
            if option in ['labels','context']:
                changeset_dict[option] = ''
            else:
                changeset_dict[option] = 'false'
    if changeset_dict['id'] == '':
        raise Exception('NO ID FOUND FOR CHANGESET: '+ line)
    return changeset_dict

def prepend_line(file_name, line):
    """ Insert given string as a new line at the beginning of a file """
    # define name of temporary dummy file
    dummy_file = file_name + '.bak'
    # open original file in read mode and dummy file in write mode
    with open(file_name, 'r') as read_obj, open(dummy_file, 'w') as write_obj:
        # Write given line to the dummy file
        write_obj.write(line + '\n')
        # Read lines from original file one by one and append them to the dummy file
        for line in read_obj:
            write_obj.write(line)
    # remove original file
    os.remove(file_name)
    # Rename dummy file as the original file
    os.rename(dummy_file, file_name)

def check_headers(file):
        file1 = open(file, 'r')
        lines = file1.readlines()
        # usage: 
        print(lines[0])
        if '--liquibase formatted sql' not in lines[0]:
            # add --liquibase formatted sql to header
            prepend_line(file, '--liquibase formatted sql')

def increment_changeset(file):
    n = 1
    for line in fileinput.input(file, inplace=1):
        #print(line)
        if '--changeset' in line:
            if '.sql' in line:
                line = line.replace('.sql-x', f'.sql-{n}')
                line = line.replace('.sql ', f'.sql-{n} ')
                n+=1
            if file.split('/')[-1] not in line:
                line = re.sub('(?<=:)\S+\.sql', file.split('/')[-1], line)
        sys.stdout.write(line)

def find_missing_changesets(file):
        file1 = open(file, 'r')
        lines = file1.readlines()
        no_changesets = True
        for line in lines:
            if 'changeset' in line:
                no_changesets = False
                break
        if no_changesets == True:
            print(f'FILE {file} CONTAINS NO CHANGESETS!')

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
    find_missing_changesets(sql_file)
    
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

