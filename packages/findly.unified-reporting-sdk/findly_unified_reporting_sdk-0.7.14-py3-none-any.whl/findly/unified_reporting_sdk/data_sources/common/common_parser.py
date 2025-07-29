import re
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

from typing import List, Optional, Callable, Tuple, Any, TypedDict
from findly.unified_reporting_sdk.protos.findly_semantic_layer_pb2 import (
    QueryArgs,
    DateStrRange,
)
from findly.unified_reporting_sdk.data_sources.common.date_range_helper import (
    create_fallback_date_range,
    parse_date_str_to_datetime,
)

NONE_VALUE = "none"
RESERVED_TOTAL = "RESERVED_TOTAL"


class DefaultFormattedDateRange(TypedDict):
    since: str
    until: str


def format_date_range_default(
    start_date: datetime, end_date: datetime
) -> DefaultFormattedDateRange:
    return {
        "since": start_date.strftime("%Y-%m-%d"),
        "until": end_date.strftime("%Y-%m-%d"),
    }


class CommonParser:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_date_ranges(
        date_str_range_list: Optional[List[DateStrRange]] = None,
        format_function: Callable[
            [datetime, datetime], Any
        ] = format_date_range_default,
    ) -> Any:
        fallback_start_date, fallback_end_date = create_fallback_date_range()

        if date_str_range_list is None or date_str_range_list == "":
            return [format_function(fallback_start_date, fallback_end_date)]

        if len(date_str_range_list) == 0:
            raise ValueError("date_str_range_list cannot be empty")

        def mapper(date_str_range: DateStrRange) -> Tuple[datetime, datetime]:
            def create_candidate_date(date_str: str) -> Optional[datetime]:
                if not date_str or date_str.lower() == NONE_VALUE:
                    return None
                return parse_date_str_to_datetime(date_str)

            start_date_str = date_str_range.start_date
            end_date_str = date_str_range.end_date

            start_date_candidate = create_candidate_date(start_date_str)
            end_date_candidate = create_candidate_date(end_date_str)

            if start_date_candidate is None and end_date_candidate is None:
                raise ValueError("Both start and end dates cannot be None")
            elif start_date_candidate is None:
                assert end_date_candidate
                start_date = end_date_candidate - relativedelta(years=1)
                end_date = end_date_candidate
            elif end_date_candidate is None:
                start_date = start_date_candidate
                end_date = datetime.now()
            else:
                if start_date_candidate > end_date_candidate:
                    raise ValueError("Start date cannot be greater than end date")
                start_date = start_date_candidate
                end_date = end_date_candidate

            return start_date, end_date

        date_ranges_tuple = [
            mapper(date_str_range) for date_str_range in date_str_range_list
        ]

        # Sort the date_ranges list in descending order based on end_date
        # If the end_date is the same, sort in descending order based on start_date
        date_ranges_tuple.sort(key=lambda x: (x[1], x[0]), reverse=True)
        date_ranges = [
            format_function(start_date, end_date)
            for start_date, end_date in date_ranges_tuple
        ]

        return date_ranges

    async def parse_query_args_to_sql(self, query: QueryArgs) -> str:
        """
        Parses the QueryArgs object into a SQL query.

        Args:
            query (QueryArgs): The query args object.

        Returns:
            str: The SQL query generated from the QueryArgs object.
        """
        query_parts = []

        select_parts = []
        # Metrics and Metrics Expression
        if query.metrics:
            select_parts.append(", ".join(query.metrics))
        elif query.metrics_expression:
            select_parts.append(", ".join(query.metrics_expression))
        if query.group_by_columns:
            select_parts.append(", ".join(query.group_by_columns))
        if len(select_parts) > 0:
            select_str = "SELECT " + ", ".join(select_parts)
            query_parts.append(select_str)

        # Where clause
        conditions = []
        if query.where_clause:
            where_clause_modified = re.sub(
                r"\bwhere\b", "", query.where_clause, flags=re.IGNORECASE
            ).strip()
            conditions.append(f"WHERE {where_clause_modified}")

        # Date Where clause
        if query.date_ranges:
            for date_range in list(query.date_ranges):
                start_date = date_range.start_date
                end_date = date_range.end_date
                # Check if start and end dates are the same
                if start_date == end_date:
                    # Use equality condition when dates are the same
                    conditions.append(f"date = '{start_date}'")
                else:
                    # Use BETWEEN when dates are different
                    conditions.append(f"date BETWEEN '{start_date}' AND '{end_date}'")

        if conditions:
            query_parts.append(f"{' AND '.join(conditions)}")

        # Group By
        if query.group_by_columns:
            group_by_str = ", ".join(query.group_by_columns)
            query_parts.append(f"GROUP BY {group_by_str}")

        # Having
        if query.having_clause:
            having_clause_modified = re.sub(
                r"\bhaving\b", "", query.having_clause, flags=re.IGNORECASE
            ).strip()
            query_parts.append(f"HAVING {having_clause_modified}")

        # Order By
        if query.order_by:
            order_by_str = ", ".join(query.order_by)
            query_parts.append(f"ORDER BY {order_by_str}")

        # Limit
        if query.limit:
            query_parts.append(f"LIMIT {query.limit}")

        return "\n".join(query_parts)

    def equalize_dataframe_rows(
        self, dataframes: List[pd.DataFrame], dimensions: List[str]
    ) -> List[pd.DataFrame]:
        if len(dataframes) <= 1 or not dimensions or all(df.empty for df in dataframes):
            return dataframes

        # Check if all dimensions exist in all dataframes
        if not all(all(dim in df.columns for dim in dimensions) for df in dataframes):
            return dataframes

        # Combine all dataframes into one to get all unique combinations of dimension values
        combined_df = pd.concat(dataframes)
        unique_combinations = combined_df[dimensions].drop_duplicates()

        # Create a list to store the equalized dataframes
        equalized_dataframes = []

        # For each dataframe, merge it with the DataFrame of unique combinations
        for i, df in enumerate(dataframes):
            equalized_df = pd.merge(unique_combinations, df, how="left", on=dimensions)
            equalized_df["origin"] = i
            equalized_dataframes.append(equalized_df)

        # Sort the combined dataframe by the 'origin' column to preserve the original order
        combined_df = pd.concat(equalized_dataframes)
        combined_df.sort_values(by="origin", inplace=True)

        # Split the combined dataframe back into individual dataframes
        equalized_dataframes = [
            df.drop(columns="origin").reset_index(drop=True)
            for _, df in combined_df.groupby("origin")
        ]

        # Ensure that rows with RESERVED_TOTAL are always the last row in each dataframe
        for df in equalized_dataframes:
            df["sort"] = df.index
            for dimension in dimensions:
                df["sort"] = df["sort"].where(
                    df[dimension] != RESERVED_TOTAL, df["sort"] + len(df)
                )
            df.sort_values(by="sort", inplace=True)
            df.drop("sort", axis=1, inplace=True)
            df.reset_index(drop=True, inplace=True)

        return equalized_dataframes
