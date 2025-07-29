import logging
import json
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any
from google.protobuf.json_format import ParseDict
from facebook_business.adobjects.adsinsights import AdsInsights

from findly.unified_reporting_sdk.data_sources.common.common_parser import (
    CommonParser,
    RESERVED_TOTAL,
)

from findly.unified_reporting_sdk.data_sources.common.where_string_comparison import (
    parse_where_column_condition,
    WhereClauseInformation,
)

from findly.unified_reporting_sdk.protos.findly_semantic_layer_pb2 import (
    Metric,
    MetricValueType,
    Dimension,
    QueryArgs,
)
import os

LOGGER = logging.getLogger(__name__)
script_path = os.path.realpath(__file__)
METRICS_JSONL_PATH = os.path.join(
    os.path.dirname(script_path), "metadata", "metrics.jsonl"
)
DIMENSION_JSONL_PATH = os.path.join(
    os.path.dirname(script_path), "metadata", "dimensions.jsonl"
)

FB_ADS_ORDER_ASC = "_ascending"
FB_ADS_ORDER_DESC = "_descending"

START_DATE_COLUMN_NAME = "date_start"
END_DATE_COLUMN_NAME = "date_stop"

DIMENSION_DIFFERENT_NAME_FILTER = [
    "account_id",
    "account_name",
    "campaign_id",
    "campaign_name",
    "adset_id",
    "adset_name",
    "ad_id",
    "ad_name",
]

# TODO (jutogashi): figure out missing operators
# NOT operator is being handled in the parse_where_column_condition function
CONVERTER_SQLGLOT_FB_FILTER_OP = {
    "eq": "EQUAL",
    "neq": "NOT_EQUAL",
    "gt": "GREATER_THAN",
    "ge": "GREATER_THAN_OR_EQUAL",
    "lt": "LESS_THAN",
    "le": "LESS_THAN_OR_EQUAL",
    "between": "IN_RANGE",
    "in": "IN",
    # "any": "ANY",
    # "all": "ALL",
    # "after": "AFTER",
    # "before": "BEFORE",
    # "onorafter": "ON_OR_AFTER",
    # "onorbefore": "ON_OR_BEFORE",
    # "none": "NONE", -> I don't know what this one should mean
    # "top": "TOP", -> already coverd in the limit
}

ACTION_VALUE_COL_NAME = "value"
DATE = "date"
YEARMONTH = "yearMonth"
N_CHAR_YEAR_MONTH = 7


def convert_in_range_to_array(range_str: str) -> Optional[List[int]]:
    # Value of IN_RANGE should be a list of min and max
    # convert value like ""300000' AND '400000"" to ["300000", "400000"]
    range_list_str = range_str.split("AND")
    # try to convert every element of the list to int
    # if it fails, return None
    try:
        range_list = [int(x) for x in range_list_str]
        return range_list
    except ValueError:
        return None


class FbAdsQueryArgsParser(CommonParser):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def default(
        cls,
    ) -> "FbAdsQueryArgsParser":
        return cls()

    def split_dataframe_by_date_ranges(
        self,
        df: pd.DataFrame,
        date_ranges: List[Dict[str, str]],
        metrics_names: List[str],
        date_dimensions: List[str],
    ) -> List[pd.DataFrame]:
        """
        Splits a DataFrame into multiple DataFrames based on specified date ranges.
        If a date range is not present, a copy of the original DataFrame is returned
        with specified metrics columns replaced by NaN values.

        Parameters:
            df (pd.DataFrame): The original DataFrame, which must contain 'date_start' and 'date_stop' columns.
            date_ranges (List[Dict[str, str]]): A list of dictionaries. Each dictionary must have 'since' and 'until' keys,
            with the values representing the start and end dates of a range, respectively.
            metrics_names (List[str]): A list of column names to be replaced with NaN if the date range is not present.
            date_dimensions (List[str]): A list of date dimensions to be added to the DataFrame.

        Returns:
            List[pd.DataFrame]: A list of DataFrames. Each DataFrame corresponds to one date range from date_ranges.
        """
        split_dfs = []
        for date_range in date_ranges:
            date_start = date_range["since"]
            date_stop = date_range["until"]
            temp_df = df[
                (df[START_DATE_COLUMN_NAME] == date_start)
                & (df[END_DATE_COLUMN_NAME] == date_stop)
            ]
            if temp_df.empty:
                # If the date range is missing from the data, we copy the original df
                # Remove the date columns and replace the metrics columns with NaN
                # and remove duplicates in case we had >2 date ranges
                temp_df = df.copy().drop(
                    columns=[START_DATE_COLUMN_NAME, END_DATE_COLUMN_NAME]
                )
                temp_df[metrics_names] = np.nan
                temp_df = temp_df.drop_duplicates().reset_index(drop=True)

            else:
                # Check here to fix problemns with time dimensions
                if DATE in date_dimensions:
                    if date_start == date_stop:
                        temp_df[DATE] = date_start
                    else:
                        temp_df[DATE] = np.nan
                elif YEARMONTH in date_dimensions:
                    if date_start[:N_CHAR_YEAR_MONTH] == date_stop[:N_CHAR_YEAR_MONTH]:
                        temp_df[YEARMONTH] = date_start[:N_CHAR_YEAR_MONTH]
                    else:
                        temp_df[YEARMONTH] = np.nan

                temp_df = temp_df.drop(
                    columns=[START_DATE_COLUMN_NAME, END_DATE_COLUMN_NAME]
                )
            split_dfs.append(temp_df)
        return split_dfs

    async def parse_report_response_to_dataframe(
        self,
        report_response: List[AdsInsights],
        query_args: QueryArgs,
    ) -> List[pd.DataFrame]:
        """
        Parses a list of AdsInsights objects into a list of pandas DataFrames.

        Parameters:
            report_response (List[AdsInsights]): A list with Facebook AdsInsights for the query performed.
            query_args (QueryArgs): An object containing the parts of a query.

        Returns:
            List[pd.DataFrame]: A list of pandas DataFrames representing the parsed report response. Each DataFrame corresponds to a specific date range.

        Raises:
            Exception: If an error occurs during the parsing process, an exception is logged and an empty DataFrame is returned.
        """
        LOGGER.info(
            {
                "msg": "parse_report_response_to_dataframe",
            }
        )
        if not report_response:
            LOGGER.info(
                {
                    "msg": "empty_report_response",
                }
            )
            return [pd.DataFrame()]

        metrics_headers = list(query_args.metrics)
        dimensions_headers = list(query_args.group_by_columns)
        date_dimensions = [
            dim for dim in [DATE, YEARMONTH] if dim in dimensions_headers
        ]
        dimensions_headers = [
            dim for dim in dimensions_headers if dim not in [DATE, YEARMONTH]
        ]

        try:
            LOGGER.info(
                {
                    "msg": "converting_to_df",
                }
            )
            df = pd.DataFrame(report_response)

            LOGGER.info(
                {
                    "msg": "sucefully_converted_to_df",
                }
            )

            # First, chack if all the metrics and dimensions are in the response
            # If not, we will fill the column with NaN
            # List the columns
            expected_columns = metrics_headers + dimensions_headers
            column_names_list = df.columns.tolist()
            # if there are only the dates columns, return empty dataframe
            if column_names_list == [START_DATE_COLUMN_NAME, END_DATE_COLUMN_NAME]:
                LOGGER.info(
                    {
                        "msg": "only_dates_columns_in_report_response",
                    }
                )
                return [pd.DataFrame()]

            # Find items in your_list that are not in column_names_list
            missing_items = [
                col for col in expected_columns if col not in column_names_list
            ]
            missing_action: List[str] = []
            if len(missing_items) > 0:
                LOGGER.info(
                    {
                        "msg": "missing_columns_in_report_response",
                        "missing_columns": missing_items,
                    }
                )
                # Add each missing item as a new column with NaN values
                for col in missing_items:
                    # action breakdowns won't show as they are nested in the response
                    # But we should check them later if they are really nested
                    if "action" in col:
                        missing_action.append(col)
                    else:
                        df[col] = np.nan

            # if more than the expected columns are in the response, remove them
            # this happens when we only send breakdowns in the query
            for col in column_names_list:
                if col not in expected_columns and col not in [
                    START_DATE_COLUMN_NAME,
                    END_DATE_COLUMN_NAME,
                ]:
                    LOGGER.info(
                        {
                            "msg": "removing_unexpected_column",
                            "column": col,
                        }
                    )
                    df.drop(columns=[col], inplace=True)

            # Now, Check if any of the metrics is of type METRIC_VALUE_TYPE_LIST_ADS_ACTION_STATS
            # If so, we want to explode the values of that column
            try:
                all_metrics_list = self.parse_metrics()
            except Exception as e:
                LOGGER.error(
                    {
                        "msg": "error_parsing_metrics",
                        "error": str(e),
                    }
                )
                return [pd.DataFrame()]
            metrics_list = [
                metric for metric in all_metrics_list if metric.name in metrics_headers
            ]

            for metric in metrics_list:
                if (
                    metric.value_type
                    == MetricValueType.METRIC_VALUE_TYPE_LIST_ADS_ACTION_STATS
                    and metric.name not in missing_items
                ):
                    LOGGER.info(
                        {
                            "msg": "struct_type_metric_found",
                            "metric": metric.name,
                        }
                    )
                    # Explode the metric column
                    exploded_df = df.explode(metric.name)

                    # Normalize the dictionary in 'metric column to separate columns
                    normalized_df = pd.json_normalize(exploded_df[metric.name].tolist())

                    # Identify overlapping columns
                    overlapping_columns = list(
                        set(exploded_df.columns).intersection(normalized_df.columns)
                    )

                    if len(overlapping_columns) > 0:
                        # Merge the normalized data with the original dataframe (excluding the metric.name column)
                        df = (
                            exploded_df.drop(metric.name, axis=1)
                            .reset_index(drop=True)
                            .merge(normalized_df, on=overlapping_columns, how="outer")
                        )
                    else:
                        df = (
                            exploded_df.drop(metric.name, axis=1)
                            .reset_index(drop=True)
                            .join(normalized_df)
                        )

                    # rename the "value" column to the original action metric name
                    if ACTION_VALUE_COL_NAME in df.columns:
                        df.rename(
                            columns={ACTION_VALUE_COL_NAME: metric.name}, inplace=True
                        )

                    # Check here if any action breakdown is really missing
                    for action_breakdown in missing_action:
                        if action_breakdown not in df.columns:
                            df[action_breakdown] = np.nan

            # remove duplicates from explosions and reset index
            df = df.drop_duplicates().reset_index(drop=True)

            # At last, return that if there is only one date range,
            # else, we need to split the dataframe into multiple dataframes
            parsed_dates = self.get_date_ranges(
                date_str_range_list=list(query_args.date_ranges),
            )
            if len(parsed_dates) == 1:
                LOGGER.info(
                    {
                        "msg": "one_date_range",
                        "parsed_dates": parsed_dates,
                    }
                )
                if date_dimensions == [DATE]:
                    LOGGER.info(
                        {
                            "msg": "time_increment_1",
                        }
                    )
                    # This will be the case when we have a result for each day
                    # Will be easier for the user to understand
                    # And consistent with GA4 for the code interpreter
                    df["date"] = df[START_DATE_COLUMN_NAME]
                    df = df.drop(columns=[START_DATE_COLUMN_NAME, END_DATE_COLUMN_NAME])

                elif date_dimensions == [YEARMONTH]:
                    LOGGER.info(
                        {
                            "msg": "time_increment_monthly",
                        }
                    )
                    # This will be the case when we have a result for each month
                    # Will be easier for the user to understand
                    df["yearMonth"] = df[START_DATE_COLUMN_NAME].str.slice(
                        0, N_CHAR_YEAR_MONTH
                    )
                    df = df.drop(columns=[START_DATE_COLUMN_NAME, END_DATE_COLUMN_NAME])
                else:
                    LOGGER.info(
                        {
                            "msg": "no_time_increment",
                        }
                    )
                    return [
                        df.drop(columns=[START_DATE_COLUMN_NAME, END_DATE_COLUMN_NAME])
                    ]

                return [df]

            LOGGER.info(
                {
                    "msg": "split_dataframe_by_date_ranges",
                    "parsed_dates": parsed_dates,
                }
            )
            final_df_list = self.split_dataframe_by_date_ranges(
                df=df,
                date_ranges=parsed_dates,
                metrics_names=metrics_headers,
                date_dimensions=date_dimensions,
            )
            return final_df_list
        except Exception as e:
            LOGGER.error(
                {
                    "msg": "error_parse_report_response_to_dataframe",
                    "error": str(e),
                }
            )
            return [pd.DataFrame()]

    # We want to parse the FB Ads totals into a dataframe.
    # This will be used by the frontend to display the data.
    def parse_totals_to_dataframe(
        self,
        summary: Optional[Dict],
        query_args: QueryArgs,
    ) -> List[pd.DataFrame]:
        if summary is None:
            return [pd.DataFrame()]

        metrics_headers = list(query_args.metrics)
        dimensions_headers = list(query_args.group_by_columns)
        date_dimensions = [
            dim for dim in [DATE, YEARMONTH] if dim in dimensions_headers
        ]
        dimensions_headers = [
            dim for dim in dimensions_headers if dim not in [DATE, YEARMONTH]
        ]

        LOGGER.info(
            {
                "msg": "parse_totals_to_dataframe",
            }
        )

        # first we convert the summary to a dataframe, this will contains the totals of the metrics
        summary_df = pd.DataFrame.from_records([summary])

        # If any metric is missing, fill it with NaN
        missing_metrics = [
            metric for metric in metrics_headers if metric not in summary_df.columns
        ]
        for missing_metric in missing_metrics:
            summary_df[missing_metric] = np.nan

        # if more than the expected columns are in the response, remove them
        # this happens when we only send breakdowns in the query
        for col in summary_df.columns.tolist():
            if col not in metrics_headers and col not in [
                START_DATE_COLUMN_NAME,
                END_DATE_COLUMN_NAME,
            ]:
                LOGGER.info(
                    {
                        "msg": "removing_unexpected_column",
                        "column": col,
                    }
                )
                summary_df.drop(columns=[col], inplace=True)

        try:
            all_metrics_list = self.parse_metrics()
        except Exception as e:
            LOGGER.error(
                {
                    "msg": "error_parsing_metrics",
                    "error": str(e),
                }
            )
            return [pd.DataFrame()]

        metrics_list = [
            metric for metric in all_metrics_list if metric.name in metrics_headers
        ]

        # now, for the struct type metrics, we need to explode the values
        for metric in metrics_list:
            if (
                metric.value_type
                == MetricValueType.METRIC_VALUE_TYPE_LIST_ADS_ACTION_STATS
                and metric.name not in missing_metrics
            ):
                LOGGER.info(
                    {
                        "msg": "struct_type_metric_found",
                        "metric": metric.name,
                    }
                )
                # Explode the metric column
                exploded_df = summary_df.explode(metric.name)

                # Normalize the dictionary in 'metric column to separate columns
                normalized_df = pd.json_normalize(exploded_df[metric.name].tolist())

                # Identify overlapping columns
                overlapping_columns = list(
                    set(exploded_df.columns).intersection(normalized_df.columns)
                )

                # Remove duplicated columns from past explosions
                normalized_df = normalized_df.drop_duplicates()

                for col in normalized_df.columns:
                    if col in overlapping_columns:
                        normalized_df.drop(col, axis=1, inplace=True)
                    else:
                        converted_column = pd.to_numeric(
                            normalized_df[col], errors="coerce"
                        )

                        # Check if there's at least one non-NaN value in the converted column
                        if converted_column.notnull().any():
                            # If so, sum the column, ignoring NaNs (i.e., failed conversions)
                            column_sum = converted_column.sum()
                            # Replace the entire column with the sum
                            normalized_df[col] = str(column_sum)
                        else:
                            # If conversion failed for any value (entire column is NaN), set to RESERVED_TOTAL
                            normalized_df[col] = RESERVED_TOTAL

                        # rename the "value" column to the original action metric name
                        if col == ACTION_VALUE_COL_NAME:
                            normalized_df.rename(
                                columns={ACTION_VALUE_COL_NAME: metric.name},
                                inplace=True,
                            )

                # Merge the normalized data with the original dataframe (excluding the metric.name column)
                summary_df = (
                    exploded_df.drop(metric.name, axis=1)
                    .reset_index(drop=True)
                    .join(normalized_df)
                )

        # Now, for every dimension in the dimensions_headers, we need to fill the values with RESERVED_TOTAL
        for dimension in dimensions_headers:
            summary_df[dimension] = RESERVED_TOTAL

        # now, deal with the date columns
        if date_dimensions == [DATE]:
            summary_df["date"] = RESERVED_TOTAL
            summary_df = summary_df.drop(
                columns=[START_DATE_COLUMN_NAME, END_DATE_COLUMN_NAME]
            )
        elif date_dimensions == [YEARMONTH]:
            summary_df["yearMonth"] = RESERVED_TOTAL
            summary_df = summary_df.drop(
                columns=[START_DATE_COLUMN_NAME, END_DATE_COLUMN_NAME]
            )
        else:
            summary_df = summary_df.drop(
                columns=[START_DATE_COLUMN_NAME, END_DATE_COLUMN_NAME]
            )

        # remove duplicates from multiple explosions
        summary_df = summary_df.drop_duplicates()
        # Keep only the first row
        summary_df = summary_df.head(1)

        return [summary_df]

    async def parse_query_args_to_request_params(
        self,
        query_args: QueryArgs,
        property_id: str,
    ) -> Dict[str, Any]:
        fb_ads_metrics_list = list(query_args.metrics)
        LOGGER.info("sucessfully got metrics")

        all_fb_dimensions = self.parse_dimensions()
        fb_ads_dimensions_list = list(
            filter(lambda x: x.name in query_args.group_by_columns, all_fb_dimensions)
        )
        LOGGER.info("sucessfully got dimensions")

        fb_ads_date_ranges = self.get_date_ranges(
            date_str_range_list=list(query_args.date_ranges),
        )
        LOGGER.info("sucessfully got date ranges")

        fb_ads_order_by_list = await self.get_order_by(
            order_by_list=list(query_args.order_by),
            order_by_candidates=list(query_args.metrics)
            + list(query_args.group_by_columns),
        )
        LOGGER.info("sucessfully got order by")

        fb_filter: List[Dict[str, str]] = []

        fb_ads_dimension_filter_list = self.get_filter_from_expression(
            expr=query_args.where_clause
        )
        if fb_ads_dimension_filter_list is not None:
            fb_filter.extend(fb_ads_dimension_filter_list)
        LOGGER.info("sucessfully got dimension filter")

        fb_ads_metrics_filter_list = self.get_filter_from_expression(
            expr=query_args.having_clause
        )
        if fb_ads_metrics_filter_list is not None:
            fb_filter.extend(fb_ads_metrics_filter_list)

        LOGGER.info("sucessfully got metrics filter")

        LOGGER.info(
            {
                "msg": "query_parts",
                "metrics": fb_ads_metrics_list,
                "dimensions": [dimension.name for dimension in fb_ads_dimensions_list],
                "date_ranges": [
                    {"start_date": dr["since"], "end_date": dr["until"]}
                    for dr in fb_ads_date_ranges
                ],
                "dimension_filters": str(fb_ads_dimension_filter_list),
                "metric_filters": str(fb_ads_metrics_filter_list),
                "order_bys": str(fb_ads_order_by_list),
                "limit": query_args.limit,
            }
        )

        fb_ads_request = {
            "metrics_names": fb_ads_metrics_list,
            "dimensions": fb_ads_dimensions_list,
            "time_ranges": fb_ads_date_ranges,
            "filtering": fb_filter,
            "sort": fb_ads_order_by_list,
            "limit": query_args.limit,
            "time_increment": query_args.time_increment,
            "level": query_args.level,
            "ad_account_id": property_id,
        }
        return fb_ads_request

    async def get_order_by(
        self,
        order_by_list: Optional[List[str]],
        order_by_candidates: List[str],
    ) -> Optional[List[str]]:
        """
        Following Fb Ads documentation: https://developers.facebook.com/docs/marketing-api/reference/ad-account/insights/
        sort: Field to sort the result, and direction of sorting.
        You can specify sorting direction by appending "_ascending" or "_descending" to the sort field. For example, "reach_descending".
        For actions, you can sort by action type in form of "actions:<action_type>". For example, ["actions:link_click_ascending"].
        This array supports no more than one element. By default, the sorting direction is ascending.
        """

        if order_by_list is None:
            return None

        allowed_order_by_candidates = [
            candidate
            for candidate in order_by_candidates
            if candidate not in [DATE, YEARMONTH]
        ]

        for order_by_item in order_by_list:
            # We should take into account the action type in the order by
            if order_by_item.lstrip("-").split(":")[0] in allowed_order_by_candidates:
                direction = (
                    FB_ADS_ORDER_DESC
                    if order_by_item.startswith("-")
                    else FB_ADS_ORDER_ASC
                )
                return [order_by_item.lstrip("-") + direction]

        return None

    def get_filter_from_expression(
        self, expr: Optional[str]
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Following Fb Ads documentation: https://developers.facebook.com/docs/marketing-api/reference/ad-account/insights/
        Filters on the report data. This parameter is an array of filter object. Each filter object has three fields: 'field', 'operator' and 'value'.
        Valid filter operator could be ('EQUAL', 'NOT_EQUAL', 'GREATER_THAN', 'GREATER_THAN_OR_EQUAL', 'LESS_THAN', 'LESS_THAN_OR_EQUAL', 'IN_RANGE', 'NOT_IN_RANGE', 'CONTAIN', 'NOT_CONTAIN', 'IN', 'NOT_IN', 'ANY', 'ALL', 'NONE').
        """
        if not expr:
            LOGGER.info({"msg": "no_expression_provided"})
            return None
        # parse the expression
        # Remove having from the expression
        # So we can use the same parser as the where clause
        clean_expr = expr
        if expr.lower().startswith("having"):
            clean_expr = expr[7:]

        unformatted_filter_list: Optional[List[WhereClauseInformation]] = (
            parse_where_column_condition(
                where_clause_str=clean_expr,
                dialect="",
            )
        )

        if unformatted_filter_list is None:
            LOGGER.info({"msg": "no_filters_in_expression"})
            return None

        final_filter_list: List[Dict[str, Any]] = []

        for unformatted_filter in unformatted_filter_list:
            field = unformatted_filter.column_name

            # Filter account_name is not valid anymore, please use account.name instead
            if field in DIMENSION_DIFFERENT_NAME_FILTER:
                LOGGER.info(
                    {
                        "msg": "updating_column_name_for_filter",
                        "field": field,
                    }
                )
                field = field.replace("_", ".")

            operator = unformatted_filter.column_operator
            value = unformatted_filter.column_value.replace("'", "").replace('""', "")

            if operator == "like":
                # check if column_value starts, ends or stars and ends with %
                # choose operator CONTAIN, STARTS_WITH or ENDS_WITH accordingly
                # and remove % from column_value
                if unformatted_filter.is_not_condition:
                    operator = "NOT_CONTAIN"
                    value = value.replace("%", "")
                elif value.startswith("%") and value.endswith("%"):
                    operator = "CONTAIN"
                    value = value[1:-1]
                elif value.startswith("%"):
                    operator = "ENDS_WITH"
                    value = value[1:]
                elif value.endswith("%"):
                    operator = "STARTS_WITH"
                    value = value[:-1]

            else:
                operator = CONVERTER_SQLGLOT_FB_FILTER_OP[operator]

            if operator == "IN_RANGE":
                if unformatted_filter.is_not_condition:
                    operator = "NOT_IN_RANGE"
                array_value = convert_in_range_to_array(value.replace(" ", ""))
                if array_value is None:
                    LOGGER.info(
                        {
                            "msg": "error_convert_in_range_to_array",
                            "value": value,
                        }
                    )
                    continue
                final_filter_list.append(
                    {
                        "field": field,
                        "operator": operator,
                        "value": array_value,
                    }
                )
            elif operator == "IN" or operator == "NOT_IN":
                # check if field and operator IN already exists in the list
                # if so, append the value to the value list
                # else, create a new filter, converting calue to an array
                # and append it to the list
                filter_found = False
                for filter in final_filter_list:
                    if filter["field"] == field and filter["operator"] == operator:
                        filter["value"].append(value)
                        filter_found = True
                        break

                if not filter_found:
                    if unformatted_filter.is_not_condition:
                        operator = "NOT_IN"
                    final_filter_list.append(
                        {
                            "field": field,
                            "operator": operator,
                            "value": [value],
                        }
                    )

            else:
                final_filter_list.append(
                    {
                        "field": field,
                        "operator": operator,
                        "value": value,
                    }
                )

        return final_filter_list

    def parse_metrics(self) -> List[Metric]:
        try:
            metrics_list = []

            # Open the .jsonl file
            with open(METRICS_JSONL_PATH, "r") as f:
                # Iterate over each line in the file
                for line in f:
                    # Each line is a complete JSON object
                    json_obj = json.loads(line)
                    message = Metric()
                    ParseDict(json_obj, message=message)
                    metrics_list.append(message)

            return metrics_list
        except Exception as e:
            raise e

    def parse_dimensions(self) -> List[Dimension]:
        try:
            dimensions_list = []

            # Open the .jsonl file
            with open(DIMENSION_JSONL_PATH, "r") as f:
                # Iterate over each line in the file
                for line in f:
                    # Each line is a complete JSON object
                    json_obj = json.loads(line)
                    message = Dimension()
                    ParseDict(json_obj, message=message)
                    dimensions_list.append(message)

            return dimensions_list
        except Exception as e:
            raise e
