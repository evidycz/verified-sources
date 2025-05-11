from dataclasses import field
from typing import Optional, Iterator, Sequence, List, Dict, Any

import dlt
from dlt.common import pendulum
from dlt.common.typing import TDataItem
from dlt.extract import DltResource
from sklik import SklikApi

from .helpers import (
    get_filtered_accounts,
    get_setting_data,
    get_start_date,
    validate_and_format_dates, get_stats_data
)
from .settings import (
    DEFAULT_CAMPAIGN_SETTINGS_FIELDS,
    DEFAULT_GROUP_SETTINGS_FIELDS,
    DEFAULT_AD_SETTINGS_FIELDS,
    DEFAULT_BANNER_SETTINGS_FIELDS,
    DEFAULT_GROUP_STATS_FIELDS,
    STATS_PRIMARY_KEY,
    OBJECT_STATS_COLUMNS,
    DEFAULT_RESTRICTION_FILTER,
)


@dlt.source(name="seznam_sklik")
def seznam_sklik_source(access_token: str = dlt.secrets.value) -> List[DltResource]:
    sklik_api = SklikApi.init(access_token)

    @dlt.resource(name="accounts", table_name="accounts_setting", write_disposition="replace")
    def accounts(account_id: Optional[int] = None, access_type: str = "rw") -> Iterator[TDataItem]:
        yield get_filtered_accounts(sklik_api, account_id, access_type)

    @dlt.transformer(name="campaigns", data_from=accounts, table_name="campaigns_setting", write_disposition="replace")
    def campaigns(account: TDataItem, fields: Sequence[str] = DEFAULT_CAMPAIGN_SETTINGS_FIELDS) -> Iterator[TDataItem]:
        yield get_setting_data(sklik_api, account, "campaigns", list(fields))

    @dlt.transformer(name="groups", data_from=accounts, table_name="groups_setting", write_disposition="replace")
    def groups(account: TDataItem, fields: Sequence[str] = DEFAULT_GROUP_SETTINGS_FIELDS) -> Iterator[TDataItem]:
        yield get_setting_data(sklik_api, account, "groups", list(fields))

    @dlt.transformer(name="ads", data_from=accounts, table_name="ads_setting", write_disposition="replace")
    def ads(account: TDataItem, fields: Sequence[str] = DEFAULT_AD_SETTINGS_FIELDS) -> Iterator[TDataItem]:
        yield get_setting_data(sklik_api, account, "ads", list(fields))

    @dlt.transformer(name="banners", data_from=accounts, table_name="banners_setting", write_disposition="replace")
    def banners(account: TDataItem, fields: Sequence[str] = DEFAULT_BANNER_SETTINGS_FIELDS) -> Iterator[TDataItem]:
        yield get_setting_data(sklik_api, account, "banners", list(fields))

    return [
        accounts,
        accounts | campaigns,
        accounts | groups,
        accounts | ads,
        accounts | banners,
    ]


@dlt.source(name="seznam_sklik")
def seznam_sklik_incremental_source(
        access_token: str = dlt.secrets.value,
        account_id: Optional[int] = None,
        initial_load_past_days: int = 28,
        attribution_window_days_lag: int = 7,
        level: str = "groups",
        granularity: str = "daily",
        fields: Sequence[str] = DEFAULT_GROUP_STATS_FIELDS,
        restriction_filter: Dict[str, Any] = field(default_factory=lambda: DEFAULT_RESTRICTION_FILTER),
) -> DltResource:
    sklik_api = SklikApi.init(access_token)

    initial_load_start_date = pendulum.today().subtract(days=initial_load_past_days)
    initial_load_start_date_str = initial_load_start_date.isoformat()

    @dlt.resource(name="accounts", write_disposition="skip")
    def accounts(access_type: str = "rw") -> Iterator[TDataItem]:
        yield get_filtered_accounts(sklik_api,None, access_type)

    @dlt.transformer(
        data_from=accounts,
        name=f"{level}",
        table_name=f"{level}_stats",
        merge_key=STATS_PRIMARY_KEY,
        columns=OBJECT_STATS_COLUMNS,
        write_disposition="merge",
    )
    def incremental_stats(
            account: TDataItem,
            refresh_start_date: dlt.sources.incremental[str] = dlt.sources.incremental(
                "date", initial_value=initial_load_start_date_str
            ),
    ) -> Iterator[TDataItem]:
        start_date = get_start_date(refresh_start_date, attribution_window_days_lag).to_date_string()
        end_date = pendulum.now().subtract(days=1).to_date_string()

        if account_id is None or account_id == int(account["userId"]):
            yield get_stats_data(
                sklik_api, account, level, start_date, end_date, list(fields), granularity, restriction_filter
            )

    return accounts | incremental_stats


@dlt.source(name="seznam_sklik")
def seznam_sklik_stats_source(
        access_token: str = dlt.secrets.value,
        account_id: Optional[int] = None,
        start_date: str = pendulum.yesterday().subtract(days=28).to_date_string(),
        end_date: str = pendulum.yesterday().to_date_string(),
        level: str = "groups",
        granularity: str = "total",
        fields: Sequence[str] = DEFAULT_GROUP_STATS_FIELDS,
        restriction_filter: Dict[str, Any] = field(default_factory=lambda: DEFAULT_RESTRICTION_FILTER),
) -> DltResource:
    sklik_api = SklikApi.init(access_token)

    @dlt.resource(name="accounts", write_disposition="skip")
    def accounts(access_type: str = "rw") -> Iterator[TDataItem]:
        yield get_filtered_accounts(sklik_api, None, access_type)

    @dlt.transformer(
        data_from=accounts,
        name=f"{level}",
        table_name=f"{level}_stats",
        write_disposition="replace",
    )
    def total_stats(account: TDataItem) -> Iterator[TDataItem]:
        if account_id is None or account_id == int(account["userId"]):
            yield get_stats_data(
                sklik_api, account, level, start_date, end_date, list(fields), granularity, restriction_filter
            )

    return accounts | total_stats
