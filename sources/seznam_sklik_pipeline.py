from typing import Optional

import dlt

from seznam_sklik import seznam_sklik_source
from sources.seznam_sklik import seznam_sklik_incremental_source


def load_account_structure(account_id: Optional[int] = None) -> None:
    pipeline = dlt.pipeline(
        name="seznam_sklik_pipeline",
        destination="duckdb",
        dataset_name="seznam_sklik",
        progress="log",
    )

    settings_source = seznam_sklik_source()
    if account_id:
        settings_source.accounts.bind(account_id=account_id)

    load_info = pipeline.run(settings_source)
    print(load_info)


def load_only_selected_levels(*resource_names: str) -> None:
    pipeline = dlt.pipeline(
        name="seznam_sklik_pipeline",
        destination="duckdb",
        dataset_name="seznam_sklik",
        progress="log",
    )

    settings_source = seznam_sklik_source()
    load_info = pipeline.run(settings_source.with_resources(resource_names))
    print(load_info)


def load_stats(account_id: Optional[int] = None) -> None:
    pipeline = dlt.pipeline(
        name="seznam_sklik_pipeline",
        destination="duckdb",
        dataset_name="seznam_sklik",
        progress="log",
    )

    stat_source = seznam_sklik_incremental_source(account_id=account_id)
    load_info = pipeline.run(stat_source)
    print(load_info)


if __name__ == "__main__":
    # load_account_structure()
    # load_only_selected_levels("campaigns", "ads")
    load_stats()
