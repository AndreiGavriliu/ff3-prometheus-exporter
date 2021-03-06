#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import time
import json
import os
import sys
from datetime import datetime
import logging
import requests
from prometheus_client import start_http_server, Gauge, Info

# config logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)-15s %(levelname)s %(message)s')

# check and set installation BaseURL
if (not 'FF3_EXPORTER_LOGLEVEL' in os.environ) or (not os.environ['FF3_EXPORTER_LOGLEVEL']):
    FF3_EXPORTER_LOGLEVEL = 'INFO'
    logging.warning('Env FF3_EXPORTER_LOGLEVEL not found or empty. Using default Info')
else:
    if os.environ['FF3_EXPORTER_LOGLEVEL'].lower() == 'debug':
        FF3_EXPORTER_LOGLEVEL = 'DEBUG'
        logging.root.setLevel('DEBUG')
    if os.environ['FF3_EXPORTER_LOGLEVEL'].lower() == 'info':
        FF3_EXPORTER_LOGLEVEL = 'INFO'
        logging.root.setLevel('INFO')
    if os.environ['FF3_EXPORTER_LOGLEVEL'].lower() == 'error':
        FF3_EXPORTER_LOGLEVEL = 'ERROR'
        logging.root.setLevel('ERROR')
    logging.basicConfig(
        level=FF3_EXPORTER_LOGLEVEL,
        format='%(asctime)-15s %(levelname)s %(message)s')

# check and set installation BaseURL
if (not 'FF3_EXPORTER_BASEURL' in os.environ) or (not os.environ['FF3_EXPORTER_BASEURL']):
    sys.exit(logging.error('Env FF3_EXPORTER_BASEURL not found or empty'))
else:
    FF3_EXPORTER_BASEURL = os.environ['FF3_EXPORTER_BASEURL']

# set ssl verify true or false
if (not 'FF3_EXPORTER_VERIFY_SSL' in os.environ) or (not os.environ['FF3_EXPORTER_VERIFY_SSL']):
    FF3_EXPORTER_VERIFY_SSL = True
    logging.warning('Env FF3_EXPORTER_VERIFY_SSL not found or empty. Using default True')
else:
    if os.environ['FF3_EXPORTER_VERIFY_SSL'].lower() == "true":
        FF3_EXPORTER_VERIFY_SSL = True
        logging.debug('Env FF3_EXPORTER_VERIFY_SSL set to True')
    elif os.environ['FF3_EXPORTER_VERIFY_SSL'].lower() == "false":
        FF3_EXPORTER_VERIFY_SSL = False
        logging.debug('Env FF3_EXPORTER_VERIFY_SSL set to False')
        # suppress warnings
        requests.packages.urllib3.disable_warnings()
    else:
        sys.exit(logging.error('Env FF3_EXPORTER_VERIFY_SSL can only be True or False'))

# check and set installation Token
if (not 'FF3_EXPORTER_TOKEN' in os.environ) or (not os.environ['FF3_EXPORTER_TOKEN']):
    sys.exit(logging.error('Env FF3_EXPORTER_TOKEN not found or empty'))
else:
    FF3_EXPORTER_TOKEN = '{\"Authorization\": \"Bearer ' + os.environ['FF3_EXPORTER_TOKEN'] + '\"}'
    logging.debug('Authorization Header: %s', FF3_EXPORTER_TOKEN)

# check and set webserver port
if (not 'FF3_EXPORTER_PORT' in os.environ) or (not os.environ['FF3_EXPORTER_PORT']):
    FF3_EXPORTER_PORT = 8000
    logging.warning('Env FF3_EXPORTER_PORT not found or empty. Using default 8000')
else:
    FF3_EXPORTER_PORT = int(os.environ['FF3_EXPORTER_PORT'])
    logging.debug('Env FF3_EXPORTER_PORT set to %s', FF3_EXPORTER_PORT)

# check and set sleep timer
if (not 'FF3_EXPORTER_SLEEP' in os.environ) or (not os.environ['FF3_EXPORTER_SLEEP']):
    FF3_EXPORTER_SLEEP = 30
    logging.warning('Env FF3_EXPORTER_SLEEP not found or empty. Using default 30 seconds')
else:
    FF3_EXPORTER_SLEEP = int(os.environ['FF3_EXPORTER_SLEEP'])
    logging.debug('Env FF3_EXPORTER_SLEEP set to %s', FF3_EXPORTER_SLEEP)

# initialize metrics
CLIENTS_METRICS = {
    'ff3_piggybanks': Gauge(
        'ff3_piggybanks',
        'Total piggybanks count', [
            'baseurl'
        ]
    ),
    'ff3_piggybank_current_amount': Gauge(
        'ff3_piggybank_current_amount',
        'Piggybank current amount', [
            'baseurl',
            'piggybank_id',
            'piggybank_name'
        ]
    ),
    'ff3_piggybank_target_amount': Gauge(
        'ff3_piggybank_target_amount',
        'Piggybank target amount', [
            'baseurl',
            'piggybank_id',
            'piggybank_name'
        ]
    ),
    'ff3_accounts': Gauge(
        'ff3_accounts',
        'Total accounts count', [
            'baseurl'
        ]
    ),
    'ff3_transactions_by_account': Gauge(
        'ff3_transactions_by_account',
        'Total transactions by account', [
            'baseurl',
            'account_id',
            'account_name'
        ]
    ),
    'ff3_balance_by_account': Gauge(
        'ff3_balance_by_account',
        'Balance by account', [
            'baseurl',
            'account_id',
            'account_name'
        ]
    ),
    'ff3_transactions_by_category': Gauge(
        'ff3_transactions_by_category',
        'Transactions by categories', [
            'baseurl',
            'category_id',
            'category_name'
        ]
    ),
    'ff3_transactions': Gauge(
        'ff3_transactions',
        'Total transaction count', [
            'baseurl'
        ]
    ),
    'ff3_bills': Gauge(
        'ff3_bills',
        'Total bills count', [
            'baseurl'
        ]
    ),
    'ff3_categories': Gauge(
        'ff3_categories',
        'Total category count', [
            'baseurl'
        ]
    ),
    'ff3': Info(
        'ff3',
        'Details about your Firefly-III deployment', [
            'baseurl'
        ]
    )
}

def ff3():
    """
    Collect system information
    """
    logging.debug('Collecting system information')
    ff3_response = requests.get(
        '{}/api/v1/about'.format(FF3_EXPORTER_BASEURL),
        headers=json.loads(FF3_EXPORTER_TOKEN),
        verify=FF3_EXPORTER_VERIFY_SSL)
    try:
        return ff3_response.json()
    except json.decoder.JSONDecodeError:
        sys.exit(logging.error('ff3(): Response is not JSON format'))

def ff3_transactions():
    """
    get all transactions from Firefly-III
    """
    logging.debug('Getting all transactions from Firefly-III')
    ff3_transactions_response = requests.get(
        '{}/api/v1/transactions'.format(FF3_EXPORTER_BASEURL),
        headers=json.loads(FF3_EXPORTER_TOKEN),
        verify=FF3_EXPORTER_VERIFY_SSL)
    try:
        return ff3_transactions_response.json()
    except json.decoder.JSONDecodeError:
        sys.exit(logging.error('ff3(): Response is not JSON format'))

def ff3_bills():
    """
    get all bills from Firefly-III
    """
    logging.debug('Getting all bills from Firefly-III')
    ff3_bills_response = requests.get(
        '{}/api/v1/bills'.format(FF3_EXPORTER_BASEURL),
        headers=json.loads(FF3_EXPORTER_TOKEN),
        verify=FF3_EXPORTER_VERIFY_SSL)
    try:
        return ff3_bills_response.json()
    except json.decoder.JSONDecodeError:
        sys.exit(logging.error('ff3(): Response is not JSON format'))

def ff3_piggybanks():
    """
    get list of piggybanks from Firefly-III
    """
    ff3_piggybanks_response = requests.get(
        '{}/api/v1/piggy_banks'.format(FF3_EXPORTER_BASEURL),
        headers=json.loads(FF3_EXPORTER_TOKEN),
        verify=FF3_EXPORTER_VERIFY_SSL)
    try:
        return ff3_piggybanks_response.json()
    except json.decoder.JSONDecodeError:
        sys.exit(logging.error('ff3(): Response is not JSON format'))

def ff3_piggybanks_details(piggybank_id):
    """
    get piggybank details from Firefly-III
    """
    logging.debug('Getting piggybank details from Firefly-III')
    ff3_piggybanks_details_response = requests.get(
        '{}/api/v1/piggy_banks/{}'.format(
            FF3_EXPORTER_BASEURL,
            piggybank_id),
        headers=json.loads(FF3_EXPORTER_TOKEN),
        verify=FF3_EXPORTER_VERIFY_SSL)
    try:
        return ff3_piggybanks_details_response.json()
    except json.decoder.JSONDecodeError:
        sys.exit(logging.error('ff3(): Response is not JSON format'))

def ff3_accounts():
    """
    get all accounts from Firefly-III
    """
    logging.debug('Getting all accounts from Firefly-III')
    ff3_accounts_response = requests.get(
        '{}/api/v1/accounts?type=asset'.format(FF3_EXPORTER_BASEURL),
        headers=json.loads(FF3_EXPORTER_TOKEN),
        verify=FF3_EXPORTER_VERIFY_SSL)
    try:
        return ff3_accounts_response.json()
    except json.decoder.JSONDecodeError:
        sys.exit(logging.error('ff3(): Response is not JSON format'))

def ff3_accounts_details(account):
    """
    get account details from Firefly-III
    """
    logging.debug('Getting account details from Firefly-III')
    ff3_accounts_details_response = requests.get(
        '{}/api/v1/accounts/{}'.format(
            FF3_EXPORTER_BASEURL,
            account),
        headers=json.loads(FF3_EXPORTER_TOKEN),
        verify=FF3_EXPORTER_VERIFY_SSL)
    try:
        return ff3_accounts_details_response.json()
    except json.decoder.JSONDecodeError:
        sys.exit(logging.error('ff3(): Response is not JSON format'))

def ff3_transactions_by_account(account, start='%7B%7D', end='%7B%7D'):
    """
    get all account transactions Firefly-III
    """
    logging.debug('Getting all account transactions Firefly-III')
    ff3_transactions_by_account_response = requests.get(
        '{}/api/v1/accounts/{}/transactions?start={}&end={}'.format(
            FF3_EXPORTER_BASEURL,
            account,
            start,
            end),
        headers=json.loads(FF3_EXPORTER_TOKEN),
        verify=FF3_EXPORTER_VERIFY_SSL)
    try:
        return ff3_transactions_by_account_response.json()
    except json.decoder.JSONDecodeError:
        sys.exit(logging.error('ff3(): Response is not JSON format'))

def ff3_categories():
    """
    get all categories from Firefly-III
    """
    logging.debug('Getting all categories from Firefly-III')
    ff3_categories_response = requests.get(
        '{}/api/v1/categories'.format(FF3_EXPORTER_BASEURL),
        headers=json.loads(FF3_EXPORTER_TOKEN),
        verify=FF3_EXPORTER_VERIFY_SSL)
    try:
        return ff3_categories_response.json()
    except json.decoder.JSONDecodeError:
        sys.exit(logging.error('ff3(): Response is not JSON format'))

def ff3_transactions_by_category(category, start='%7B%7D', end='%7B%7D'):
    """
    get all account transactions Firefly-III
    """
    logging.debug('Getting all account transactions Firefly-III')
    ff3_transactions_by_category_response = requests.get(
        '{}/api/v1/categories/{}/transactions?start={}&end={}'.format(
            FF3_EXPORTER_BASEURL,
            category,
            start,
            end),
        headers=json.loads(FF3_EXPORTER_TOKEN),
        verify=FF3_EXPORTER_VERIFY_SSL)
    try:
        return ff3_transactions_by_category_response.json()
    except json.decoder.JSONDecodeError:
        sys.exit(logging.error('ff3(): Response is not JSON format'))

def collect():
    """
    Main function to export collected  metrics
    """
    CLIENTS_METRICS['ff3'].labels(FF3_EXPORTER_BASEURL).info({
        'version': ff3()['data']['version'],
        'api_version': ff3()['data']['version'],
        'php_version': ff3()['data']['php_version'],
        'os': ff3()['data']['os']})

    CLIENTS_METRICS['ff3_transactions'].labels(FF3_EXPORTER_BASEURL).set(
        ff3_transactions()['meta']['pagination']['total'])

    CLIENTS_METRICS['ff3_bills'].labels(FF3_EXPORTER_BASEURL).set(
        ff3_bills()['meta']['pagination']['total'])

    CLIENTS_METRICS['ff3_accounts'].labels(FF3_EXPORTER_BASEURL).set(
        ff3_accounts()['meta']['pagination']['total'])

    CLIENTS_METRICS['ff3_piggybanks'].labels(FF3_EXPORTER_BASEURL).set(
        ff3_piggybanks()['meta']['pagination']['total'])

    CLIENTS_METRICS['ff3_categories'].labels(FF3_EXPORTER_BASEURL).set(
        ff3_categories()['meta']['pagination']['total'])

    for account in ff3_accounts()['data']:
        CLIENTS_METRICS['ff3_transactions_by_account'].labels(
            FF3_EXPORTER_BASEURL,
            account['id'],
            account['attributes']['name']).set(
                ff3_transactions_by_account(
                    account=account['id'],
                    start='',
                    end='')['meta']['pagination']['total'])

    for category in ff3_categories()['data']:
        CLIENTS_METRICS['ff3_transactions_by_category'].labels(
            FF3_EXPORTER_BASEURL,
            category['id'],
            category['attributes']['name']).set(
                ff3_transactions_by_category(
                    category=category['id'],
                    start='',
                    end='')['meta']['pagination']['total'])

    for account in ff3_accounts()['data']:
        CLIENTS_METRICS['ff3_balance_by_account'].labels(
            FF3_EXPORTER_BASEURL,
            account['id'],
            account['attributes']['name']).set(
                ff3_accounts_details(
                    account=account['id'])['data']['attributes']['current_balance'])

    for piggybank in ff3_piggybanks()['data']:
        CLIENTS_METRICS['ff3_piggybank_target_amount'].labels(
            FF3_EXPORTER_BASEURL,
            piggybank['id'],
            piggybank['attributes']['name']).set(
                ff3_piggybanks_details(
                    piggybank_id=piggybank['id'])['data']['attributes']['target_amount'])

    for piggybank in ff3_piggybanks()['data']:
        CLIENTS_METRICS['ff3_piggybank_current_amount'].labels(
            FF3_EXPORTER_BASEURL,
            piggybank['id'],
            piggybank['attributes']['name']).set(
                ff3_piggybanks_details(
                    piggybank_id=piggybank['id'])['data']['attributes']['current_amount'])

if __name__ == '__main__':
    start_http_server(FF3_EXPORTER_PORT)
    while True:
        collect()
        logging.info('Fetched data')
        time.sleep(FF3_EXPORTER_SLEEP)
