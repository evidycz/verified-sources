import pytest

import dlt
import pendulum

from sources.seznam_sklik import (
    seznam_sklik_source,
    seznam_sklik_incremental_source,
    seznam_sklik_stats_source,
    get_start_date,
)
from sources.seznam_sklik.settings import DEFAULT_CAMPAIGN_STATS_FIELDS

from tests.utils import ALL_DESTINATIONS, assert_load_info, load_table_counts


@pytest.mark.skip("We don't have a Seznam Sklik test account.")
@pytest.mark.parametrize("destination_name", ALL_DESTINATIONS)
def test_load_all_sklik_objects(destination_name: str) -> None:
    pipeline = dlt.pipeline(
        pipeline_name="seznam_sklik",
        destination=destination_name,
        dataset_name="seznam_sklik_data",
        dev_mode=True,
    )
    info = pipeline.run(seznam_sklik_source())
    assert_load_info(info)
    # assert tables created
    expected_tables = ["accounts_setting", "campaigns_setting", "groups_setting", "ads_setting", "banners_setting"]
    # all those tables in the schema
    assert (
        set(expected_tables)
        - set(t["name"] for t in pipeline.default_schema.data_tables())
        == set()
    )
    # get counts
    table_counts = load_table_counts(pipeline, *expected_tables)
    # all tables loaded
    assert set(table_counts.keys()) == set(expected_tables)
    assert all(c > 0 for c in table_counts.values())


@pytest.mark.skip("We don't have a Seznam Sklik test account.")
def test_load_selected_resources() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="seznam_sklik",
        destination="duckdb",
        dataset_name="seznam_sklik_selected_data",
        dev_mode=True,
    )
    source = seznam_sklik_source()
    # Only load accounts and campaigns
    info = pipeline.run(source.with_resources("accounts", "campaigns"))
    assert_load_info(info)

    # Check that only the selected tables were created
    expected_tables = ["accounts_setting", "campaigns_setting"]
    schema_tables = [t["name"] for t in pipeline.default_schema.data_tables()]
    assert set(expected_tables) == set(schema_tables)

    # Check that data was loaded into the tables
    table_counts = load_table_counts(pipeline, *expected_tables)
    assert all(c > 0 for c in table_counts.values())


@pytest.mark.skip("We don't have a Seznam Sklik test account.")
def test_load_with_account_filter() -> None:
    # Test with a specific account ID
    pipeline = dlt.pipeline(
        pipeline_name="seznam_sklik",
        destination="duckdb",
        dataset_name="seznam_sklik_filtered_data",
        dev_mode=True,
    )

    # Use a dummy account ID for testing
    test_account_id = 12345
    source = seznam_sklik_source()
    source.accounts.bind(account_id=test_account_id)

    # This will likely not load any data since the account ID is fake
    info = pipeline.run(source)
    assert_load_info(info, expected_load_packages=0)


@pytest.mark.skip("We don't have a Seznam Sklik test account.")
def test_load_incremental_stats() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="seznam_sklik",
        destination="duckdb",
        dataset_name="seznam_sklik_incremental_data",
        dev_mode=True,
    )

    # Load stats for the last 7 days
    source = seznam_sklik_incremental_source(initial_load_past_days=7)
    info = pipeline.run(source)
    assert_load_info(info)

    # Check that the stats table was created
    expected_table = "groups_stats"
    schema_tables = [t["name"] for t in pipeline.default_schema.data_tables()]
    assert expected_table in schema_tables

    # Check that data was loaded into the table
    table_counts = load_table_counts(pipeline, expected_table)
    assert table_counts.get(expected_table, 0) > 0


@pytest.mark.skip("We don't have a Seznam Sklik test account.")
def test_load_stats_with_different_level() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="seznam_sklik",
        destination="duckdb",
        dataset_name="seznam_sklik_level_data",
        dev_mode=True,
    )

    # Load campaign level stats
    source = seznam_sklik_stats_source(level="campaigns", fields=DEFAULT_CAMPAIGN_STATS_FIELDS)
    info = pipeline.run(source)
    assert_load_info(info)

    # Check that the campaigns_stats table was created
    expected_table = "campaigns_stats"
    schema_tables = [t["name"] for t in pipeline.default_schema.data_tables()]
    assert expected_table in schema_tables


def test_get_start_date() -> None:
    # Test with an ISO datetime string
    input_value = "2023-08-09T12:30:00"
    result = get_start_date(
        incremental_start_date=dlt.sources.incremental("start_date", input_value),
        attribution_window_days_lag=7,
    )
    assert isinstance(result, pendulum.DateTime)
    assert result.year == 2023
    assert result.month == 8
    assert result.day == 2
    assert result.hour == 12
    assert result.minute == 30
    assert result.second == 0
    assert result.timezone_name == "UTC"

    # Test with an ISO date string
    input_value = "2023-08-09"
    result = get_start_date(
        incremental_start_date=dlt.sources.incremental("start_date", input_value),
        attribution_window_days_lag=7,
    )
    assert isinstance(result, pendulum.DateTime)
    assert result.year == 2023
    assert result.month == 8
    assert result.day == 2
    assert result.hour == 0
    assert result.minute == 0
    assert result.second == 0
    assert result.timezone_name == "UTC"

    # Test with a different attribution window
    input_value = "2023-08-09"
    result = get_start_date(
        incremental_start_date=dlt.sources.incremental("start_date", input_value),
        attribution_window_days_lag=14,
    )
    assert result.year == 2023
    assert result.month == 7
    assert result.day == 26