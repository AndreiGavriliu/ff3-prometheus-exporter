# ff3-prometheus-exporter
Simple Firefly-III Prometheus exporter

(Work in progress / untested changes)

## Usage

### Required
```
export FF3_EXPORTER_BASEURL="https://you-firefly-iii/base/url"
export FF3_EXPORTER_TOKEN="your-API-token"
```

### Optional
```
export FF3_EXPORTER_PORT=8000
export FF3_EXPORTER_SLEEP=30
export FF3_EXPORTER_VERIFY_SSL=False
```

# Example Result
based on https://demo.firefly-iii.org

```
$ curl localhost:8000
# HELP python_gc_objects_collected_total Objects collected during gc
# TYPE python_gc_objects_collected_total counter
python_gc_objects_collected_total{generation="0"} 361.0
python_gc_objects_collected_total{generation="1"} 0.0
python_gc_objects_collected_total{generation="2"} 0.0
# HELP python_gc_objects_uncollectable_total Uncollectable object found during GC
# TYPE python_gc_objects_uncollectable_total counter
python_gc_objects_uncollectable_total{generation="0"} 0.0
python_gc_objects_uncollectable_total{generation="1"} 0.0
python_gc_objects_uncollectable_total{generation="2"} 0.0
# HELP python_gc_collections_total Number of times this generation was collected
# TYPE python_gc_collections_total counter
python_gc_collections_total{generation="0"} 50.0
python_gc_collections_total{generation="1"} 4.0
python_gc_collections_total{generation="2"} 0.0
# HELP python_info Python platform information
# TYPE python_info gauge
python_info{implementation="CPython",major="3",minor="7",patchlevel="6",version="3.7.6"} 1.0
# HELP transactions_count_total Total transaction count
# TYPE transactions_count_total counter
transactions_count_total 446.0
# HELP bills_count_total Total bills count
# TYPE bills_count_total counter
bills_count_total 9.0
# HELP account_current_balance Current Account Balance
# TYPE account_current_balance gauge
account_current_balance{account_id="6",account_name="Cash wallet"} 0.0
account_current_balance{account_id="1",account_name="Checking Account"} 548.6
account_current_balance{account_id="5",account_name="Checking account in GBP"} 0.0
account_current_balance{account_id="4",account_name="Credit card in USD"} 0.0
account_current_balance{account_id="2",account_name="Savings Account"} 2800.0
account_current_balance{account_id="3",account_name="Shared Checking Account"} 0.0
# HELP account_transaction_count_total Total transaction count for account
# TYPE account_transaction_count_total counter
account_transaction_count_total{account_id="6",account_name="Cash wallet"} 0.0
account_transaction_count_total{account_id="1",account_name="Checking Account"} 446.0
account_transaction_count_total{account_id="5",account_name="Checking account in GBP"} 0.0
account_transaction_count_total{account_id="4",account_name="Credit card in USD"} 0.0
account_transaction_count_total{account_id="2",account_name="Savings Account"} 14.0
account_transaction_count_total{account_id="3",account_name="Shared Checking Account"} 0.0
# HELP account_transaction_count_today_total Total transaction count for account today
# TYPE account_transaction_count_today_total counter
account_transaction_count_today_total{account_id="6",account_name="Cash wallet"} 0.0
account_transaction_count_today_total{account_id="1",account_name="Checking Account"} 1.0
account_transaction_count_today_total{account_id="5",account_name="Checking account in GBP"} 0.0
account_transaction_count_today_total{account_id="4",account_name="Credit card in USD"} 0.0
account_transaction_count_today_total{account_id="2",account_name="Savings Account"} 0.0
account_transaction_count_today_total{account_id="3",account_name="Shared Checking Account"} 0.0
# HELP piggybanks_details_target_total Piggy Bank target amount
# TYPE piggybanks_details_target_total counter
piggybanks_details_target_total{piggybank_id="1",piggybank_name="New camera"} 1000.0
piggybanks_details_target_total{piggybank_id="2",piggybank_name="New phone"} 600.0
piggybanks_details_target_total{piggybank_id="3",piggybank_name="New couch"} 500.0
piggybanks_details_target_total{piggybank_id="4",piggybank_name="Lorem ipsum dolor sit amet"} 30.0
piggybanks_details_target_total{piggybank_id="5",piggybank_name="consectetur adipiscing elit"} 500.0
piggybanks_details_target_total{piggybank_id="6",piggybank_name="Suspendisse eget dolor eget"} 600.0
piggybanks_details_target_total{piggybank_id="7",piggybank_name="ipsum venenatis tincidunt"} 990.0
piggybanks_details_target_total{piggybank_id="8",piggybank_name="Integer gravida velit"} 12000.0
piggybanks_details_target_total{piggybank_id="9",piggybank_name="in orci finibus sagittis"} 200.0
piggybanks_details_target_total{piggybank_id="10",piggybank_name="Fusce porta arcu sit amet ex tincidunt"} 50.0
piggybanks_details_target_total{piggybank_id="11",piggybank_name="sit amet elementum (inactive)"} 600.0
piggybanks_details_target_total{piggybank_id="12",piggybank_name="Pellentesque dictum elit"} 123.0
piggybanks_details_target_total{piggybank_id="13",piggybank_name="Pellentesque dictum elit X"} 123.0
# HELP piggybanks_details_current_total Piggy Bank current amount
# TYPE piggybanks_details_current_total counter
piggybanks_details_current_total{piggybank_id="1",piggybank_name="New camera"} 735.0
piggybanks_details_current_total{piggybank_id="2",piggybank_name="New phone"} 333.0
piggybanks_details_current_total{piggybank_id="3",piggybank_name="New couch"} 120.0
piggybanks_details_current_total{piggybank_id="4",piggybank_name="Lorem ipsum dolor sit amet"} 0.0
piggybanks_details_current_total{piggybank_id="5",piggybank_name="consectetur adipiscing elit"} 0.0
piggybanks_details_current_total{piggybank_id="6",piggybank_name="Suspendisse eget dolor eget"} 0.0
piggybanks_details_current_total{piggybank_id="7",piggybank_name="ipsum venenatis tincidunt"} 0.0
piggybanks_details_current_total{piggybank_id="8",piggybank_name="Integer gravida velit"} 0.0
piggybanks_details_current_total{piggybank_id="9",piggybank_name="in orci finibus sagittis"} 0.0
piggybanks_details_current_total{piggybank_id="10",piggybank_name="Fusce porta arcu sit amet ex tincidunt"} 0.0
piggybanks_details_current_total{piggybank_id="11",piggybank_name="sit amet elementum (inactive)"} 0.0
piggybanks_details_current_total{piggybank_id="12",piggybank_name="Pellentesque dictum elit"} 0.0
piggybanks_details_current_total{piggybank_id="13",piggybank_name="Pellentesque dictum elit X"} 0.0
```
