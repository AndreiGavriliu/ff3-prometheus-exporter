#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Prometheus exporter for Firefly-III
Version: v0.2
API Documentation: https://api-docs.firefly-iii.org
"""

import time
import json
import os
import sys
from datetime import datetime
import requests
from prometheus_client import start_http_server, Counter, Info

# check and set installation BaseURL
if (not 'FF3_EXPORTER_BASEURL' in os.environ) or (not os.environ['FF3_EXPORTER_BASEURL']):
    sys.exit('ERROR: Env FF3_EXPORTER_BASEURL not found or empty')
else:
    FF3_EXPORTER_BASEURL = os.environ['FF3_EXPORTER_BASEURL']

# check and set installation Token
if (not 'FF3_EXPORTER_TOKEN' in os.environ) or (not os.environ['FF3_EXPORTER_TOKEN']):
    sys.exit('ERROR: Env FF3_EXPORTER_TOKEN not found or empty')
else:
    FF3_EXPORTER_TOKEN = '{\"Authorization\": \"Bearer ' + os.environ['FF3_EXPORTER_TOKEN'] + '\"}'

# check and set webserver port
if (not 'FF3_EXPORTER_PORT' in os.environ) or (not os.environ['FF3_EXPORTER_PORT']):
    print('WARNING: Env FF3_EXPORTER_PORT not found or empty. Using default 8000')
    FF3_EXPORTER_PORT = 8000
else:
    FF3_EXPORTER_PORT = int(os.environ['FF3_EXPORTER_PORT'])

# check and set sleep timer
if (not 'FF3_EXPORTER_SLEEP' in os.environ) or (not os.environ['FF3_EXPORTER_SLEEP']):
    print('WARNING: Env FF3_EXPORTER_SLEEP not found or empty. Using default 30 seconds')
    FF3_EXPORTER_SLEEP = 30
else:
    FF3_EXPORTER_SLEEP = int(os.environ['FF3_EXPORTER_SLEEP'])

# initialize metrics
CLIENTS_METRICS = {
    'ff3_piggybanks': Counter(
        'ff3_piggybanks',
        'Total piggybanks count',
        ['baseurl']),
    'ff3_piggybank_current_amount': Counter(
        'ff3_piggybank_current_amount',
        'Piggybank current amount',
        ['baseurl', 'piggybank_id', 'piggybank_name']),
    'ff3_piggybank_target_amount': Counter(
        'ff3_piggybank_target_amount',
        'Piggybank target amount',
        ['baseurl', 'piggybank_id', 'piggybank_name']),
    'ff3_accounts': Counter(
        'ff3_accounts',
        'Total accounts count',
        ['baseurl']),
    'ff3_transactions_by_account': Counter(
        'ff3_transactions_by_account',
        'Total transactions by account',
        ['baseurl', 'account_id', 'account_name']),
    'ff3_transactions': Counter(
        'ff3_transactions',
        'Total transaction count',
        ['baseurl']),
    'ff3_bills': Counter(
        'ff3_bills',
        'Total bills count', ['baseurl']),
    'ff3': Info(
        'ff3',
        'Details about your Firefly-III deployment',
        ['baseurl'])
}

def ff3():
    """
    Collect system information
    """
    ff3_response = requests.get(
        '{}/api/v1/about'.format(FF3_EXPORTER_BASEURL),
        headers=json.loads(FF3_EXPORTER_TOKEN))
    try:
        return ff3_response.json()
    except json.decoder.JSONDecodeError:
        sys.exit('ff3(): Response is not JSON format')

def ff3_transactions():
    """
    get all transactions from Firefly-III
    """
    ff3_transactions_response = requests.get(
        '{}/api/v1/transactions'.format(FF3_EXPORTER_BASEURL),
        headers=json.loads(FF3_EXPORTER_TOKEN))
    try:
        return ff3_transactions_response.json()
    except json.decoder.JSONDecodeError:
        sys.exit('ff3_transactions(): Response is not JSON format')

def ff3_bills():
    """
    get all bills from Firefly-III
    """
    ff3_bills_response = requests.get(
        '{}/api/v1/bills'.format(FF3_EXPORTER_BASEURL),
        headers=json.loads(FF3_EXPORTER_TOKEN))
    try:
        return ff3_bills_response.json()
    except json.decoder.JSONDecodeError:
        sys.exit('ff3_bills(): Response is not JSON format')

def ff3_piggybanks():
    """
    get list of piggybanks from Firefly-III
    """
    ff3_piggybanks_response = requests.get(
        '{}/api/v1/piggy_banks'.format(FF3_EXPORTER_BASEURL),
        headers=json.loads(FF3_EXPORTER_TOKEN))
    try:
        return ff3_piggybanks_response.json()
    except json.decoder.JSONDecodeError:
        sys.exit('ff3_piggybanks(): Response is not JSON format')

def ff3_piggybanks_details(piggybank_id):
    """
    get piggybank details from Firefly-III
    """
    ff3_piggybanks_details_response = requests.get(
        '{}/api/v1/piggy_banks/{}'.format(
            FF3_EXPORTER_BASEURL,
            piggybank_id),
        headers=json.loads(FF3_EXPORTER_TOKEN))
    try:
        return ff3_piggybanks_details_response.json()
    except json.decoder.JSONDecodeError:
        sys.exit('ff3_piggybanks_details(): Response is not JSON format')

def ff3_accounts():
    """
    get all accounts from Firefly-III
    """
    ff3_accounts_response = requests.get(
        '{}/api/v1/accounts?type=asset'.format(FF3_EXPORTER_BASEURL),
        headers=json.loads(FF3_EXPORTER_TOKEN))
    try:
        return ff3_accounts_response.json()
    except json.decoder.JSONDecodeError:
        sys.exit('ff3_accounts(): Response is not JSON format')

def ff3_transactions_by_account(account, start='%7B%7D', end='%7B%7D'):
    """
    get all account transactions
    """
    ff3_transactions_by_account_response = requests.get(
        '{}/api/v1/accounts/{}/transactions?start={}&end={}'.format(
            FF3_EXPORTER_BASEURL,
            account,
            start,
            end),
        headers=json.loads(FF3_EXPORTER_TOKEN))
    try:
        return ff3_transactions_by_account_response.json()
    except json.decoder.JSONDecodeError:
        sys.exit('ff3_transactions_by_account(): Response is not JSON format')

def collect():
    """
    Main function to export collected  metrics
    """
    CLIENTS_METRICS['ff3'].labels(FF3_EXPORTER_BASEURL).info({
        'version': ff3()['data']['version'],
        'api_version': ff3()['data']['version'],
        'php_version': ff3()['data']['php_version'],
        'os': ff3()['data']['os']})

    CLIENTS_METRICS['ff3_transactions'].labels(FF3_EXPORTER_BASEURL).inc(
        ff3_transactions()['meta']['pagination']['total'])

    CLIENTS_METRICS['ff3_bills'].labels(FF3_EXPORTER_BASEURL).inc(
        ff3_bills()['meta']['pagination']['total'])

    CLIENTS_METRICS['ff3_accounts'].labels(FF3_EXPORTER_BASEURL).inc(
        ff3_accounts()['meta']['pagination']['total'])

    CLIENTS_METRICS['ff3_piggybanks'].labels(FF3_EXPORTER_BASEURL).inc(
        ff3_piggybanks()['meta']['pagination']['total'])

    for account in ff3_accounts()['data']:
        CLIENTS_METRICS['ff3_transactions_by_account'].labels(
            FF3_EXPORTER_BASEURL,
            account['id'],
            account['attributes']['name']).inc(
                ff3_transactions_by_account(
                    account=account['id'],
                    start='',
                    end='')['meta']['pagination']['total'])

    for piggybank in ff3_piggybanks()['data']:
        CLIENTS_METRICS['ff3_piggybank_target_amount'].labels(
            FF3_EXPORTER_BASEURL,
            piggybank['id'],
            piggybank['attributes']['name']).inc(
                ff3_piggybanks_details(
                    piggybank_id=piggybank['id'])['data']['attributes']['target_amount'])

    for piggybank in ff3_piggybanks()['data']:
        CLIENTS_METRICS['ff3_piggybank_current_amount'].labels(
            FF3_EXPORTER_BASEURL,
            piggybank['id'],
            piggybank['attributes']['name']).inc(
                ff3_piggybanks_details(
                    piggybank_id=piggybank['id'])['data']['attributes']['current_amount'])

if __name__ == '__main__':
    start_http_server(8000, 'localhost')
    while True:
        collect()
        print('Checked API: {}'.format(datetime.now().strftime("%Y-%m-%d @ %H:%M:%S.%f")))
        time.sleep(FF3_EXPORTER_SLEEP)
