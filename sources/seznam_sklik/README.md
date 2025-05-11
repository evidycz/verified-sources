
# Seznam Sklik

This Seznam Sklik dlt verified source and pipeline example loads data to a preferred destination using the Seznam Sklik API. Seznam Sklik is an advertising platform by Seznam.cz, a popular search engine and web portal in the Czech Republic.

The following resources are available for loading data with this verified source:

| Resource | Description |
| --- | --- |
| accounts | Information about user accounts with access to Seznam Sklik |
| campaigns | Advertising campaigns that focus on specific objectives or goals |
| groups | Groups of ads within a campaign |
| ads | Individual text advertisements created and displayed within an ad group |
| banners | Visual advertisements with specific dimensions |

And stats resources:

| Resource          | Description |
|---| --- |
| incremental_stats | Suitable for regular updates of campaign data.|
| total_stats       | For one-time export of data from campaigns.|

## Initialize the Seznam Sklik verified source and pipeline example

```bash
dlt init seznam_sklik duckdb
```

Here, we chose DuckDB as the destination. Alternatively, you can also choose `redshift`, `bigquery`, or any of the other [destinations](https://dlthub.com/docs/dlt-ecosystem/destinations/).

## Grab Seznam Sklik credentials

You need to obtain an access token from Seznam Sklik to use this verified source.

## Add credentials

1. Open `.dlt/secrets.toml`.
2. Enter the `access_token`:

    ```toml
    # put your secret values and credentials here. do not share this file and do not push it to github
    [sources.seznam_sklik]
    access_token="set me up!"
    ```

3. Enter credentials for your chosen destination as per the [docs](https://dlthub.com/docs/dlt-ecosystem/destinations/).

## Run the pipeline example

1. Install the necessary dependencies by running the following command:

    ```bash
    pip install -r requirements.txt
    ```

2. Now the pipeline can be run by using the command:

    ```bash
    python seznam_sklik_pipeline.py
    ```

3. To make sure that everything is loaded as expected, use the command:

    ```bash
    dlt pipeline <pipeline_name> show
    ```

    For example, the pipeline_name for the above pipeline example is `seznam_sklik`, but you may also use any custom name instead.

## Available Sources

This verified source provides three main ways to load data:

1. **seznam_sklik_source**: Loads account settings data including campaigns, groups, ads, and banners.
2. **seznam_sklik_incremental_source**: Loads incremental stats data with attribution window support.
3. **seznam_sklik_stats_source**: Loads stats data for a specific time period.

### Example: Loading Settings Data

```python
import dlt
from seznam_sklik import seznam_sklik_source

pipeline = dlt.pipeline(
    pipeline_name="seznam_sklik",
    destination="duckdb",
    dataset_name="seznam_sklik_data"
)

data = seznam_sklik_source()
info = pipeline.run(data)
print(info)
```

### Example: Loading Incremental Stats Data

```python
import dlt
from seznam_sklik import seznam_sklik_incremental_source

pipeline = dlt.pipeline(
    pipeline_name="seznam_sklik",
    destination="duckdb",
    dataset_name="seznam_sklik_data"
)

data = seznam_sklik_incremental_source(
    initial_load_past_days=28,
    attribution_window_days_lag=7,
    level="groups",
    granularity="daily"
)
info = pipeline.run(data)
print(info)
```
