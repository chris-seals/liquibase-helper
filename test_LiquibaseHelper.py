import os
import pytest
import LiquibaseHelper

def test_changeset_parser_partial():
    expected_dict = {
        'id':'auth:id:sql-1',
        'runAlways':'false',
        'runOnChange':'true',
        'labels':'v1.3.0',
        'contexts':'',
        'runWith':'sqlplus'
        }
    input_changeset = '--changeset auth:id:sql-1 runWith:sqlplus runOnChange:true labels:v1.3.0'
    assert LiquibaseHelper.changeset_parser(input_changeset) == expected_dict


def test_changeset_parser_full():
    expected_dict = {
        'id': 'auth:id:sql-2',
        'runAlways': 'false',
        'runOnChange': 'true',
        'labels': 'v1.3.0',
        'contexts': 'maws-mid-release',
        'runWith':'sqlplus'
    }
    input_changeset = '--changeset auth:id:sql-2 runWith:sqlplus runOnChange:true labels:v1.3.0 contexts:maws-mid-release '
    assert LiquibaseHelper.changeset_parser(input_changeset) == expected_dict
