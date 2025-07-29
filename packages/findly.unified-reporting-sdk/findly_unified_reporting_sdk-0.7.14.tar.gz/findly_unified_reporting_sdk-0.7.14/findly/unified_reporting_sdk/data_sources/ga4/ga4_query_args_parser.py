import logging
from datetime import datetime
import pandas as pd
import numpy as np
from google.analytics.data_v1beta.types import (
    Metric,
    Dimension,
    FilterExpression,
    Filter,
    OrderBy,
    NumericValue,
    FilterExpressionList,
    RunReportResponse,
    DateRange,
)
from typing import Dict, Any, List, Optional
from findly.unified_reporting_sdk.data_sources.common.common_parser import (
    CommonParser,
    RESERVED_TOTAL,
)
from findly.unified_reporting_sdk.protos.findly_semantic_layer_pb2 import QueryArgs

LOGGER = logging.getLogger(__name__)

DATE_FORMATS = {
    "date": ("%Y%m%d", "%Y-%m-%d"),
    "dateHour": ("%Y%m%d%H", "%Y-%m-%d %H"),
    "dateHourMinute": ("%Y%m%d%H%M", "%Y-%m-%d %H:%M"),
    "firstSessionDate": ("%Y%m%d", "%Y-%m-%d"),
    "yearMonth": ("%Y%m", "%Y-%m"),
}

DATE_RANGE_HEADER = "dateRange"


def format_ga4_date_ranges_default(
    start_date: datetime, end_date: datetime
) -> DateRange:
    return DateRange(
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
    )


class GA4QueryArgsParser(CommonParser):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def default(
        cls,
    ) -> "GA4QueryArgsParser":
        return cls()

    # We want to parse the GA4 response into a dataframe.
    # This will be used by the frontend to display the data.
    def parse_report_response_to_dataframe(
        self,
        report_response: RunReportResponse,
    ) -> List[pd.DataFrame]:
        # Get the dimension and metric headers.
        dimension_headers = [dh.name for dh in report_response.dimension_headers]
        metric_headers = [mh.name for mh in report_response.metric_headers]

        # Get the rows.
        rows = []
        for row in report_response.rows:
            row_dict: Dict[str, Any] = {}
            for i, header in enumerate(dimension_headers):
                value = row.dimension_values[i].value
                if header in DATE_FORMATS:
                    ga_format, output_format = DATE_FORMATS[header]
                    try:
                        parsed_date = datetime.strptime(value, ga_format)
                        value = parsed_date.strftime(output_format)
                    except ValueError:
                        # Handle or log the error as needed
                        pass
                row_dict[header] = value

            for i, header in enumerate(metric_headers):
                value = row.metric_values[i].value
                # Check if the metric header ends with 'Rate'
                if header.endswith("Rate"):
                    # Convert the value to a float and multiply by 100
                    value_number = float(value) * 100
                else:
                    # Cap float values to 2 decimal places
                    value_number = float(value)
                    if value_number.is_integer():
                        value_number = int(value_number)
                    else:
                        value_number = value_number
                row_dict[header] = value_number

            rows.append(row_dict)

        if len(rows) == 0:
            df = pd.DataFrame(rows)
            return [df]

        # if the rows contain a dateRange header, we want to remove it.
        # the header is specified by the DATE_RANGE_HEADER constant.
        # the values in the columns are in the format date_range_index, e.g. date_range_0, date_range_1, date_range_2, ...
        # we want to transform it in a sorted list of dataframes based on the index.
        # we want to remove the dateRange header from the dataframe.
        if DATE_RANGE_HEADER in rows[0]:
            # Get the unique date range indices.
            date_range_indices = set([row[DATE_RANGE_HEADER] for row in rows])

            # Create a list of dataframes.
            dataframes_tuple: List[tuple[int, pd.DataFrame]] = []
            for date_range_index in date_range_indices:
                # Create a dataframe with the rows that have the same date range index.
                date_range_df = pd.DataFrame(
                    [row for row in rows if row[DATE_RANGE_HEADER] == date_range_index]
                )

                # Remove the dateRange header.
                date_range_df = date_range_df.drop(columns=[DATE_RANGE_HEADER])

                # Add the dataframe to the list of dataframes.
                dataframes_tuple.append(
                    (int(str(date_range_index).split("_")[-1]), date_range_df)
                )
            # Sort the dataframes based on the date range index.
            dataframes_tuple.sort()

            # Remove the date range index from the tuples.
            dataframes: List[pd.DataFrame] = [df for _, df in dataframes_tuple]

            # remove DATE_RANGE_HEADER from the dimension headers.
            if DATE_RANGE_HEADER in dimension_headers:
                dimension_headers.remove(DATE_RANGE_HEADER)

            return dataframes

        return [pd.DataFrame(rows)]

    # We want to parse the GA4 totals into a dataframe.
    # This will be used by the frontend to display the data.
    def parse_totals_to_dataframe(
        self,
        report_response: RunReportResponse,
    ) -> List[pd.DataFrame]:
        # Get the dimension and metric headers.
        dimension_headers = [dh.name for dh in report_response.dimension_headers]
        metric_headers = [mh.name for mh in report_response.metric_headers]

        # Get the rows.
        rows = []

        for date_range_index, row in enumerate(report_response.totals):
            row_dict: Dict[str, Any] = {}
            for i, header in enumerate(dimension_headers):
                if i < len(row.dimension_values):
                    row_dict[header] = row.dimension_values[i].value
                elif header == DATE_RANGE_HEADER:
                    row_dict[header] = f"date_range_{date_range_index}"
                else:
                    row_dict[header] = RESERVED_TOTAL

            for i, header in enumerate(metric_headers):
                if i < len(row.metric_values):
                    value = row.metric_values[i].value
                    # Check if the metric header ends with 'Rate'
                    if header.endswith("Rate"):
                        # Convert the value to a float, multiply by 100, and format it with '%'
                        value = "{:.2f}".format(float(value) * 100)
                    else:
                        # Cap float values to 2 decimal places
                        float_value = float(value)
                        if not float_value.is_integer():
                            value = "{:.2f}".format(float_value)
                    row_dict[header] = value
                else:
                    row_dict[header] = np.nan

            rows.append(row_dict)

        if len(rows) == 0:
            df = pd.DataFrame(rows)
            return [df]

        # if the rows contain a dateRange header, we want to remove it.
        # the header is specified by the DATE_RANGE_HEADER constant.
        # the values in the columns are in the format date_range_index, e.g. date_range_0, date_range_1, date_range_2, ...
        # we want to transform it in a sorted list of dataframes based on the index.
        # we want to remove the dateRange header from the dataframe.
        if DATE_RANGE_HEADER in rows[0]:
            # Get the unique date range indices.
            date_range_indices = set([row[DATE_RANGE_HEADER] for row in rows])

            # Create a list of dataframes.
            dataframes_tuple: List[tuple[int, pd.DataFrame]] = []
            for date_range_index in date_range_indices:
                # Create a dataframe with the rows that have the same date range index.
                date_range_df = pd.DataFrame(
                    [row for row in rows if row[DATE_RANGE_HEADER] == date_range_index]
                )

                # Remove the dateRange header.
                date_range_df = date_range_df.drop(columns=[DATE_RANGE_HEADER])

                # Add the dataframe to the list of dataframes.
                dataframes_tuple.append(
                    (int(str(date_range_index).split("_")[-1]), date_range_df)
                )
            # Sort the dataframes based on the date range index.
            dataframes_tuple.sort()

            # Remove the date range index from the tuples.
            dataframes: List[pd.DataFrame] = [df for _, df in dataframes_tuple]

            # remove DATE_RANGE_HEADER from the dimension headers.
            if DATE_RANGE_HEADER in dimension_headers:
                dimension_headers.remove(DATE_RANGE_HEADER)

            return dataframes

        return [pd.DataFrame(rows)]

    async def parse_query_args_to_request_params(
        self,
        query_args: QueryArgs,
        property_id: str,
    ) -> Dict[str, Any]:
        # Remove duplicates from metrics and dimensions to avoid redundant processing.
        unique_metrics = list(dict.fromkeys(query_args.metrics))
        unique_dimensions = list(dict.fromkeys(query_args.group_by_columns))

        ga4_metrics_list = await self.get_metrics(
            metrics_name_list=unique_metrics,
        )
        LOGGER.info("sucessfully got metrics")

        ga4_dimensions_list = await self.get_dimensions(
            dimensions_name_list=unique_dimensions,
        )
        LOGGER.info("sucessfully got dimensions")

        ga4_date_ranges = self.get_date_ranges(
            date_str_range_list=(
                list(query_args.date_ranges)
                if query_args.date_ranges is not None
                else None
            ),
            format_function=format_ga4_date_ranges_default,
        )
        LOGGER.info("sucessfully got date ranges")

        ga4_order_by_list = await self.get_order_by(
            order_by_list=(
                list(query_args.order_by) if query_args.order_by is not None else None
            ),
            order_by_metrics_candidates=list(query_args.metrics),
            order_by_dimensions_candidates=list(query_args.group_by_columns),
        )
        LOGGER.info("sucessfully got order by")

        ga4_dimension_filter_list = await self.get_filter_clause(
            filter_clause=query_args.where_clause
        )
        LOGGER.info("sucessfully got dimension filter")

        ga4_metrics_filter_list = await self.get_filter_clause(
            filter_clause=query_args.having_clause
        )
        LOGGER.info("sucessfully got metrics filter")

        LOGGER.info(
            {
                "msg": "query_parts",
                "metrics": [metric.name for metric in ga4_metrics_list],
                "dimensions": [dimension.name for dimension in ga4_dimensions_list],
                "date_ranges": [
                    {"start_date": dr.start_date, "end_date": dr.end_date}
                    for dr in ga4_date_ranges
                ],
                "dimension_filters": str(ga4_dimension_filter_list),
                "metric_filters": str(ga4_metrics_filter_list),
                "order_bys": str(ga4_order_by_list),
                "limit": query_args.limit,
            }
        )

        ga4_request = {
            "metrics": ga4_metrics_list,
            "dimensions": ga4_dimensions_list,
            "date_ranges": ga4_date_ranges,
            "dimension_filter": ga4_dimension_filter_list,
            "metric_filter": ga4_metrics_filter_list,
            "order_bys": ga4_order_by_list,
            "limit": query_args.limit or None,
            "offset": None,
            "property_id": property_id,
        }
        return ga4_request

    # TODO: Allow metric expressions or more complex metrics.
    async def get_dimensions(self, dimensions_name_list: List[str]) -> List[Dimension]:
        if len(dimensions_name_list) == 0:
            return []

        dimensions_list = [
            Dimension(
                name=dimension_name,
            )
            for dimension_name in dimensions_name_list
        ]

        return dimensions_list

    async def get_metrics(self, metrics_name_list: List[str]) -> List[Metric]:
        if len(metrics_name_list) == 0:
            return []

        metrics_list = [
            Metric(
                name=metric_name,
            )
            for metric_name in metrics_name_list
        ]

        return metrics_list

    async def get_order_by(
        self,
        order_by_list: Optional[List[str]],
        order_by_metrics_candidates: List[str],
        order_by_dimensions_candidates: List[str],
    ) -> Optional[List[OrderBy]]:
        """
        This method parses the order_by string and returns a list of OrderBy objects.

        Args:
            order_by (Optional[List[str]]): A string specifying the order of the results.
                This should be in the format: "order_by_name_1, order_by_name_2, order_by_name_3, ...",
                with a "-" sign before the name to specify reverse order when needed.
                The ordering matters: order_by_name_1 is the most important, and order_by_name_n is the least important.
            order_by_metrics_candidates (List[str]): A list of possible metrics that can be used for ordering.
            order_by_dimensions_candidates (List[str]): A list of possible dimensions that can be used for ordering.

        Returns:
            Optional[List[OrderBy]]: A list of OrderBy objects representing the order of the results.
                Each OrderBy object can be a MetricOrderBy, DimensionOrderBy, or PivotOrderBy.
                For example, if order_by is "-ds, country, -city",
                the returned list might be [OrderBy(metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"), desc=True)].
                If order_by is None or an empty string, returns None.

        Note:
            A "-" sign can be used to specify reverse order, e.g. "-ds".
            This will be used for the GA4 API.
        """
        order_bys: List[OrderBy] = []

        for order_by in order_by_list or []:
            if order_by.startswith("-"):
                order_by = order_by[1:]
                if order_by in order_by_metrics_candidates:
                    order_bys.append(
                        OrderBy(
                            metric=OrderBy.MetricOrderBy(
                                metric_name=order_by,
                            ),
                            desc=True,
                        )
                    )
                elif order_by in order_by_dimensions_candidates:
                    order_bys.append(
                        OrderBy(
                            dimension=OrderBy.DimensionOrderBy(
                                dimension_name=order_by,
                            ),
                            desc=True,
                        )
                    )
            else:
                if order_by in order_by_metrics_candidates:
                    order_bys.append(
                        OrderBy(
                            metric=OrderBy.MetricOrderBy(
                                metric_name=order_by,
                            ),
                            desc=False,
                        )
                    )
                elif order_by in order_by_dimensions_candidates:
                    order_bys.append(
                        OrderBy(
                            dimension=OrderBy.DimensionOrderBy(
                                dimension_name=order_by,
                            ),
                            desc=False,
                        )
                    )

        return order_bys

    async def get_filter_clause(
        self, filter_clause: Optional[str]
    ) -> Optional[FilterExpression]:
        """
        Asynchronously parses a WHERE or HAVING clause string into a FilterExpression object.

        Args:
            filter_clause (str): The WHERE or HAVING clause string to be parsed.

        Returns:
            Optional[FilterExpression]: A FilterExpression object representing the parsed WHERE clause
                or None if the filter_clause is None or empty.
        """
        if filter_clause is None or filter_clause.strip() == "":
            return None

        filter_clause = filter_clause.replace("WHERE", "").strip()
        filter_clause = filter_clause.replace("HAVING", "").strip()

        def parse_expression(expression: str) -> FilterExpression:
            expression = expression.strip()
            # Base case: if the expression doesn't contain logical operators, create a simple filter.
            if all(
                operator not in expression for operator in ["AND", "OR", "NOT", "("]
            ):
                return create_filter_expression(expression)

            # If the expression starts with an open parenthesis, find its corresponding close parenthesis
            if "(" in expression:
                open_parenthesis_index = expression.find("(")
                close_parenthesis_index = find_closing_parenthesis(expression)

                # If the opening parenthesis is at the start, parse the nested expression and the remainder separately
                if open_parenthesis_index == 0:
                    nested_expression = expression[1:close_parenthesis_index]
                    remainder_expression = expression[
                        close_parenthesis_index + 1 :
                    ].strip()

                    # Recursively process the remainder after dealing with the nested expression
                    parsed_nested = parse_expression(nested_expression)

                    # If there's a remainder after the closing parenthesis, handle it
                    if remainder_expression:
                        if remainder_expression.startswith("AND "):
                            return FilterExpression(
                                and_group=FilterExpressionList(
                                    expressions=[
                                        parsed_nested,
                                        parse_expression(
                                            remainder_expression[4:].strip()
                                        ),
                                    ]
                                )
                            )
                        elif remainder_expression.startswith("OR "):
                            return FilterExpression(
                                or_group=FilterExpressionList(
                                    expressions=[
                                        parsed_nested,
                                        parse_expression(
                                            remainder_expression[3:].strip()
                                        ),
                                    ]
                                )
                            )

                    else:
                        return parsed_nested

            if " AND " in expression:
                parts = expression.split(" AND ")
                return FilterExpression(
                    and_group=FilterExpressionList(
                        expressions=[parse_expression(part.strip()) for part in parts]
                    )
                )

            if " OR " in expression:
                parts = expression.split(" OR ")
                return FilterExpression(
                    or_group=FilterExpressionList(
                        expressions=[parse_expression(part.strip()) for part in parts]
                    )
                )

            return create_filter_expression(expression)

        def create_filter_expression(part: str) -> FilterExpression:
            part = part.strip()
            if "NOT " in part:
                # Remove 'NOT' and the following space
                return FilterExpression(
                    not_expression=create_simple_filter(part.replace("NOT", "").strip())
                )
            return create_simple_filter(part)

        def create_simple_filter(part: str) -> FilterExpression:
            part = part.strip()

            # Handling the IN clause
            if " IN " in part:
                field, in_values_str = part.split(" IN ")
                in_values_str = in_values_str.strip("() ")
                in_values = [
                    v.strip().strip("'").strip("`") for v in in_values_str.split(",")
                ]
                return FilterExpression(
                    filter=Filter(
                        field_name=field.strip().strip("`"),
                        in_list_filter=Filter.InListFilter(
                            values=in_values,
                            case_sensitive=False,
                        ),
                    )
                )

            part = part.lstrip("(").rstrip(")")

            # Handling the BETWEEN clause
            if " BETWEEN " in part:
                field, range_values_str = part.split(" BETWEEN ")
                from_value_str, to_value_str = [
                    v.strip() for v in range_values_str.split(" AND ")
                ]
                from_value = create_numeric_value(from_value_str)
                to_value = create_numeric_value(to_value_str)
                return FilterExpression(
                    filter=Filter(
                        field_name=field.strip().strip("`"),
                        between_filter=Filter.BetweenFilter(
                            fromValue=from_value, toValue=to_value
                        ),
                    )
                )

            # Handling the LIKE clause
            if " LIKE " in part:
                field, like_value = part.split(" LIKE ")
                field = field.strip()
                like_value = like_value.strip().replace("'", "")

                # Determine the match type based on the pattern
                if like_value.startswith("%") and like_value.endswith("%"):
                    match_type = Filter.StringFilter.MatchType.CONTAINS
                    like_value = like_value.strip("%")
                elif like_value.startswith("%"):
                    match_type = Filter.StringFilter.MatchType.ENDS_WITH
                    like_value = like_value.strip("%")
                elif like_value.endswith("%"):
                    match_type = Filter.StringFilter.MatchType.BEGINS_WITH
                    like_value = like_value.strip("%")
                else:
                    # If there is no wildcard, it's an exact match
                    match_type = Filter.StringFilter.MatchType.EXACT

                return FilterExpression(
                    filter=Filter(
                        field_name=field.strip().strip("`"),
                        string_filter=Filter.StringFilter(
                            value=like_value,
                            match_type=match_type,
                            case_sensitive=False,
                        ),
                    )
                )

            operators = {
                "<=": "LESS_THAN_OR_EQUAL",
                ">=": "GREATER_THAN_OR_EQUAL",
                "!=": "NOT_EQUAL",  # Check for != before =
                "<>": "NOT_EQUAL",  # Check for <> before <
                "<": "LESS_THAN",
                ">": "GREATER_THAN",
                "=": "EQUAL",
            }

            for symbol, op_name in operators.items():
                if symbol in part:
                    field, value = part.split(symbol)
                    field = field.strip()
                    value = value.strip().strip("'")
                    # Check if the value is numeric
                    if is_numeric(value):
                        numeric_value = create_numeric_value(value)

                        if op_name == "NOT_EQUAL":
                            return FilterExpression(
                                filter=Filter(
                                    field_name=field.strip().strip("`"),
                                    not_expression=FilterExpression(
                                        filter=Filter(
                                            field_name=field.strip().strip("`"),
                                            numeric_filter=Filter.NumericFilter(
                                                operation="EQUAL",
                                                value=numeric_value,
                                            ),
                                        )
                                    ),
                                )
                            )

                        return FilterExpression(
                            filter=Filter(
                                field_name=field.strip().strip("`"),
                                numeric_filter=Filter.NumericFilter(
                                    operation=op_name, value=numeric_value
                                ),
                            )
                        )

            match_operators = {
                "!=": "NOT_EQUAL",  # Check for != before =
                "<>": "NOT_EQUAL",
                "=": "EQUAL",
            }

            for symbol, op_name in match_operators.items():
                if symbol in part:
                    field, value = part.split(symbol)
                    field = field.strip()
                    value = value.strip().replace("'", "")

                    # Check if the value is a boolean
                    if value.lower() in ["true", "false"]:
                        value = str(value.lower() == "true").lower()

                    if op_name == "NOT_EQUAL":
                        return FilterExpression(
                            not_expression=FilterExpression(
                                filter=Filter(
                                    field_name=field.strip().strip("`"),
                                    string_filter=Filter.StringFilter(
                                        value=value.strip().strip("`"),
                                        case_sensitive=False,
                                    ),
                                )
                            )
                        )
                    else:
                        return FilterExpression(
                            filter=Filter(
                                field_name=field.strip().strip("`"),
                                string_filter=Filter.StringFilter(
                                    value=value.strip().strip("`")
                                ),
                            )
                        )

            value = value.strip().replace("'", "")
            return FilterExpression(
                filter=Filter(
                    field_name=field.strip().strip("`"),
                    string_filter=Filter.StringFilter(value=value.strip().strip("`")),
                )
            )

        def is_numeric(value: str) -> bool:
            try:
                # Try to convert the value to an integer or float
                int(value)
                return True
            except ValueError:
                try:
                    float(value)
                    return True
                except ValueError:
                    return False

        def create_numeric_value(value: str) -> NumericValue:
            """
            Create a NumericValue object based on the input string.

            Args:
                value (str): The input string representing the numeric value.

            Returns:
                NumericValue: The created NumericValue object.

            Examples:
                >>> create_numeric_value("10")
                NumericValue(int64_value=10)

                >>> create_numeric_value("3.14")
                NumericValue(double_value=3.14)
            """
            if "." in value:
                return NumericValue(double_value=float(value))
            return NumericValue(int64_value=int(value))

        def find_closing_parenthesis(s: str) -> int:
            stack = []
            for i, c in enumerate(s):
                if c == "(":
                    stack.append(i)
                elif c == ")":
                    stack.pop()
                    if not stack:
                        return i
            return -1

        try:
            return parse_expression(filter_clause)

        except Exception as e:
            # WHERE Clause is not in valid format
            return None

    async def get_column_names_from_filter_expression(
        self,
        filter_expression: Optional[FilterExpression],
    ) -> List[str]:
        if not filter_expression:
            return []

        filter_column_names: List[str] = []

        # check the and_group
        # if it is not empty, recursively call this function on each filter
        if filter_expression.and_group and filter_expression.and_group.expressions:
            for filter in filter_expression.and_group.expressions:
                filter_column_names.extend(
                    await self.get_column_names_from_filter_expression(filter)
                )

        # check the or_group
        # if it is not empty, recursively call this function on each filter
        if filter_expression.or_group and filter_expression.or_group.expressions:
            for filter in filter_expression.or_group.expressions:
                filter_column_names.extend(
                    await self.get_column_names_from_filter_expression(filter)
                )

        # check the not_expression
        # if it is not empty, recursively call this function on the filter
        if filter_expression.not_expression:
            filter_column_names.extend(
                await self.get_column_names_from_filter_expression(
                    filter_expression.not_expression
                )
            )

        # check the filter
        # if it is not empty, add the column name to the list
        if filter_expression.filter:
            filter_column_names.append(filter_expression.filter.field_name)

        return filter_column_names
