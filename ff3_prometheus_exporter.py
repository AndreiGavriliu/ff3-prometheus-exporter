"""
Prometheus Exporter for your Firefly-III installation
"""
import os
import sys
import time
import json
from datetime import datetime
from calendar import monthrange
import requests
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server

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
    FF3_EXPORTER_PORT = os.environ['FF3_EXPORTER_PORT']

# check and set sleep timer
if (not 'FF3_EXPORTER_SLEEP' in os.environ) or (not os.environ['FF3_EXPORTER_SLEEP']):
    print('WARNING: Env FF3_EXPORTER_SLEEP not found or empty. Using default 30 seconds')
    FF3_EXPORTER_SLEEP = 30
else:
    FF3_EXPORTER_SLEEP = os.environ['FF3_EXPORTER_SLEEP']

CURRENT_DAY = datetime.today().strftime("%Y-%m-%d")
CURRENT_MONTH_START = datetime.today().strftime("%Y-%m") + '-01'
CURRENT_MONTH_END = monthrange(
    int(datetime.today().strftime("%Y")),
    int(datetime.today().strftime("%-m")))[1]

class CustomCollector():
    """
    standard metrics collection class
    """
    # def __init__(self):
    #     pass

    def collect(self):
        """
        standard metrics collection function
        """
        # get transactions
        transactions = ff3_transactions()
        transactions_counter = CounterMetricFamily(
            'transactions_count',
            'Total transaction count')
        transactions_counter.add_metric([
            'transactions_count'], transactions[
                "meta"][
                    "pagination"][
                        "total"])
        yield transactions_counter

        # get bills
        bills = ff3_bills()
        bills_counter = CounterMetricFamily(
            'bills_count',
            'Total bills count')
        bills_counter.add_metric([
            'bills_count'], bills[
                "meta"][
                    "pagination"][
                        "total"])
        yield bills_counter

        # get accounts
        accounts = ff3_accounts()
        accounts = accounts['data']

        # get account balances
        account_balance_gauge = GaugeMetricFamily(
            'account_current_balance',
            'Current Account Balance',
            labels=[
                'account_id',
                'account_name'])
        for account in accounts:
            if account['attributes']['type'] == 'asset':
                account_balance_gauge.add_metric([
                    account['id'],
                    account['attributes']['name']], account[
                        'attributes'][
                            'current_balance'])
        yield account_balance_gauge

        # get account transactions count (total)
        account_transaction_counter = CounterMetricFamily(
            'account_transaction_count',
            'Total transaction count for account',
            labels=[
                'account_id',
                'account_name'])
        for account in accounts:
            if account['attributes']['type'] == 'asset':
                accounts_transactions = ff3_accounts_transactions(
                    account=account['id'],
                    start='',
                    end='')
                account_transaction_counter.add_metric([
                    account['id'],
                    account['attributes']['name']], accounts_transactions[
                        'meta'][
                            'pagination'][
                                'total'])
        yield account_transaction_counter

        # get account transactions count (today)
        account_transaction_today_counter = CounterMetricFamily(
            'account_transaction_count_today',
            'Total transaction count for account today',
            labels=[
                'account_id',
                'account_name'])
        for account in accounts:
            if account['attributes']['type'] == 'asset':
                ff3_accounts_transactions_daily = ff3_accounts_transactions(
                    account=account['id'],
                    start=CURRENT_DAY,
                    end=CURRENT_DAY)
                account_transaction_today_counter.add_metric([
                    account['id'],
                    account['attributes']['name']], ff3_accounts_transactions_daily[
                        'meta'][
                            'pagination'][
                                'total'])
        yield account_transaction_today_counter

        # get piggybank target_amount
        piggybanks = ff3_piggybanks()
        piggybanks = piggybanks['data']

        # get piggybank target amount
        piggybanks_details_target_amount = CounterMetricFamily(
            'piggybanks_details_target',
            'Piggy Bank target amount',
            labels=[
                'piggybank_id',
                'piggybank_name'])

        for piggybank in piggybanks:
            ff3_piggybanks_details_target_amount = ff3_piggybanks_details(
                piggybank_id=piggybank['id'])
            piggybanks_details_target_amount.add_metric([
                piggybank['id'],
                piggybank['attributes']['name']], ff3_piggybanks_details_target_amount[
                    'data'][
                        'attributes'][
                            'target_amount'])
        yield piggybanks_details_target_amount

        # get piggybank current amount
        piggybanks_details_current_amount = CounterMetricFamily(
            'piggybanks_details_current',
            'Piggy Bank current amount',
            labels=[
                'piggybank_id',
                'piggybank_name'])

        for piggybank in piggybanks:
            ff3_piggybanks_details_current_amount = ff3_piggybanks_details(
                piggybank_id=piggybank['id'])
            piggybanks_details_current_amount.add_metric([
                piggybank['id'],
                piggybank['attributes']['name']], ff3_piggybanks_details_current_amount[
                    'data'][
                        'attributes'][
                            'current_amount'])
        yield piggybanks_details_current_amount

if __name__ == '__main__':

    def ff3_transactions():
        """
        get all transactions from Firefly-III
        """
        transactions = requests.get(
            '{}/api/v1/transactions'.format(FF3_EXPORTER_BASEURL),
            headers=json.loads(FF3_EXPORTER_TOKEN))
        try:
            transactions = transactions.json()
            return transactions
        except json.decoder.JSONDecodeError:
            sys.exit('ff3_transactions(): Response is not JSON format')

    def ff3_accounts():
        """
        get all accounts from Firefly-III
        """
        accounts = requests.get(
            '{}/api/v1/accounts'.format(FF3_EXPORTER_BASEURL),
            headers=json.loads(FF3_EXPORTER_TOKEN))
        try:
            accounts = accounts.json()
            return accounts
        except json.decoder.JSONDecodeError:
            sys.exit('ff3_accounts(): Response is not JSON format')

    def ff3_accounts_transactions(account, start='%7B%7D', end='%7B%7D'):
        """
        get all account transactions
        """
        account_transactions = requests.get(
            '{}/api/v1/accounts/{}/transactions?start={}&end={}'.format(
                FF3_EXPORTER_BASEURL,
                account,
                start,
                end),
            headers=json.loads(FF3_EXPORTER_TOKEN))
        try:
            account_transactions = account_transactions.json()
            return account_transactions
        except json.decoder.JSONDecodeError:
            sys.exit('ff3_accounts_transactions(): Response is not JSON format')

    def ff3_bills():
        """
        get list of bills
        """
        bills = requests.get(
            '{}/api/v1/bills'.format(FF3_EXPORTER_BASEURL),
            headers=json.loads(FF3_EXPORTER_TOKEN))
        try:
            bills = bills.json()
            return bills
        except json.decoder.JSONDecodeError:
            sys.exit('ff3_bills(): Response is not JSON format')

    # TODO: get list of bills transactions /api/v1/bills/{id}/transactions
    # def ff3_bills_transactions():
    #     """
    #     get transactions related to bills
    #     """

    def ff3_piggybanks():
        """
        get list of piggybanks
        """
        piggybanks = requests.get(
            '{}/api/v1/piggy_banks'.format(FF3_EXPORTER_BASEURL),
            headers=json.loads(FF3_EXPORTER_TOKEN))
        try:
            piggybanks = piggybanks.json()
            return piggybanks
        except json.decoder.JSONDecodeError:
            sys.exit('ff3_piggybanks(): Response is not JSON format')

    def ff3_piggybanks_details(piggybank_id):
        """
        get piggybank details
        """
        piggybank_details = requests.get(
            '{}/api/v1/piggy_banks/{}'.format(
                FF3_EXPORTER_BASEURL,
                piggybank_id),
            headers=json.loads(FF3_EXPORTER_TOKEN))
        try:
            piggybank_details = piggybank_details.json()
            return piggybank_details
        except json.decoder.JSONDecodeError:
            sys.exit('ff3_piggybanks_details(): Response is not JSON format')

    start_http_server(FF3_EXPORTER_PORT)
    REGISTRY.register(CustomCollector())
    while True:
        print('Checked API: {}'.format(datetime.now().strftime("%Y-%m-%d @ %H:%M:%S.%f")))
        time.sleep(FF3_EXPORTER_SLEEP)
