import asyncio
import backoff
import json
from aiocache import cached, Cache
from google.protobuf.json_format import ParseDict
from google.analytics.data_v1beta import BetaAnalyticsDataAsyncClient
from google.analytics.admin_v1beta import AnalyticsAdminServiceAsyncClient
from google.analytics.admin_v1beta.types import (
    ListDataStreamsRequest,
    DataStream,
    GetPropertyRequest,
)
from google.analytics.data_v1beta.types import (
    DateRange,
    Metric,
    MetricType,
    Dimension,
    FilterExpression,
    OrderBy,
    MetricAggregation,
    RunReportRequest,
    RunReportResponse,
    GetMetadataRequest,
    Metadata,
    MetricMetadata,
    DimensionMetadata,
    Compatibility,
    CheckCompatibilityRequest,
    CheckCompatibilityResponse,
)

from findly.unified_reporting_sdk.data_sources.common.entities import (
    ReportsClientQueryResult,
)
from findly.unified_reporting_sdk.protos.findly_semantic_layer_pb2 import (
    Dimension as DimensionProto,
)
from findly.unified_reporting_sdk.protos.findly_semantic_layer_pb2 import (
    Metric as MetricProto,
)
from findly.unified_reporting_sdk.protos.findly_semantic_layer_pb2 import (
    MetricValueType,
    QueryArgs,
)
from google.api_core.exceptions import InvalidArgument, ResourceExhausted
from typing import Any, List, Optional, Tuple, Dict

import logging
import os
from google.oauth2.credentials import Credentials
from findly.unified_reporting_sdk.data_sources.common.reports_client import (
    ReportsClient,
)
from findly.unified_reporting_sdk.data_sources.ga4.ga4_query_args_parser import (
    GA4QueryArgsParser,
)

COHORT_CATEGORY = "cohort"

# default ga4 dimensions values
EMPTY_STRING = ""
NOT_SET_VALUE = "(not set)"

SESSIONS_METRIC = Metric(name="sessions")

ORDER_BY_SESSIONS = OrderBy(
    metric=OrderBy.MetricOrderBy(metric_name="sessions"),
    desc=True,
)

REQUEST_TIMEOUT = 30

LOGGER = logging.getLogger(__name__)

GA4_PARSER = GA4QueryArgsParser.default()

script_path = os.path.realpath(__file__)
DIMENSION_JSONL_PATH = os.path.join(
    os.path.dirname(script_path), "metadata", "dimensions.jsonl"
)

# Configure the logging for 'backoff' module to WARNING level or higher
logging.getLogger("backoff").setLevel(logging.WARNING)


def give_up(exc: Any) -> bool:
    return isinstance(exc, InvalidArgument)


def load_common_dimensions_from_json() -> Optional[List[DimensionProto]]:
    dimensions_list = []

    with open(DIMENSION_JSONL_PATH, "r") as f:
        for line_number, line in enumerate(f, 1):
            try:
                json_obj = json.loads(line)
                message = DimensionProto()
                ParseDict(json_obj, message=message)
                dimensions_list.append(message)
            except json.JSONDecodeError as e:
                LOGGER.error(f"Error parsing line {line_number}: {e}")
                return None

    return dimensions_list


COMMON_DIMENSIONS = load_common_dimensions_from_json()


class GA4Client(ReportsClient):
    def __init__(
        self,
        token: str,
        client_id: str,
        client_secret: str,
    ):
        creds = Credentials(
            token=None,
            refresh_token=token,
            client_id=client_id,
            client_secret=client_secret,
            token_uri="https://oauth2.googleapis.com/token",
        )

        self._client = BetaAnalyticsDataAsyncClient(credentials=creds)
        self._admin_client = AnalyticsAdminServiceAsyncClient(credentials=creds)

    @cached(ttl=3600, cache=Cache.MEMORY)  # Cache results for 1 hr
    async def _decorated_list_property_ids(self, **kwargs: str) -> Optional[List[str]]:
        """Lists all GA4 properties accessible to the authenticated user.

        Returns:
            List[str] or None: A list of property IDs if properties are found, None otherwise.
        """
        try:
            # Make the reques
            page_result = await self._admin_client.list_account_summaries()
            property_ids = []
            # Handle the response
            async for response in page_result:
                for property_summary in response.property_summaries:
                    property_ids.append(property_summary.property.strip("properties/"))

            if not property_ids:
                LOGGER.error(
                    {
                        "msg": "no_properties_found",
                    }
                )
                return None
            LOGGER.info(
                {
                    "msg": "properties_found",
                    "property_ids": property_ids,
                }
            )
            return property_ids

        except Exception as e:
            LOGGER.error(
                {
                    "msg": "failed_to_list_properties",
                    "error": str(e),
                }
            )
            return None

    async def list_property_ids(self, **kwargs: str) -> Optional[List[str]]:
        return await self._decorated_list_property_ids(**kwargs)

    @cached(ttl=3600, cache=Cache.MEMORY)  # Cache results for 1 hour
    async def _decorated_get_domain_name(
        self, property_id: str, **kwargs: str
    ) -> Optional[str]:
        """Retrieves the domain name for a given GA4 property.

        Returns:
            str or None: The primary domain name for the property ID if found, None otherwise.
        """
        try:
            property_path = f"properties/{property_id}"  # Ensure correct format
            request = ListDataStreamsRequest(parent=property_path)
            response = await self._admin_client.list_data_streams(request=request)

            # Extract domain names
            domain_names = []
            for stream in response.data_streams:
                if stream.type_ == DataStream.DataStreamType.WEB_DATA_STREAM:
                    domain_name = stream.web_stream_data.default_uri
                    if domain_name:  # Ensure that the domain name is not None or empty
                        domain_names.append(domain_name)
                        LOGGER.info(f"Found domain name: {domain_name}")

            if not domain_names:
                LOGGER.info(f"No domain names found for property ID {property_id}")
                return None

            # Assuming first domain name is the primary one
            # TODO: (jutogashi) Add support for multiple domain names
            primary_domain = domain_names[0]
            LOGGER.info(
                f"Primary domain name for property ID {property_id}: {primary_domain}"
            )
            return primary_domain

        except Exception as e:
            LOGGER.error(
                {
                    "msg": f"Failed to retrieve domain name for property ID {property_id}",
                    "error": str(e),
                }
            )
            return None

    async def get_domain_name(self, property_id: str, **kwargs: str) -> Optional[str]:
        return await self._decorated_get_domain_name(property_id=property_id, **kwargs)

    async def get_property_timezone(
        self, property_id: str, **kwargs: str
    ) -> Optional[str]:
        try:
            # Create a request for the specific property
            request = GetPropertyRequest(name=f"properties/{property_id}")

            # Fetch the property details
            response = await self._admin_client.get_property(request)

            # Extract the timezone from the response
            timezone = response.time_zone if response.time_zone else "Timezone not set"
            LOGGER.info(
                f"Timezone for property ID {property_id}: {timezone}",
            )
            return timezone
        except Exception as e:
            LOGGER.error(
                {
                    "msg": f"Failed to retrieve timezone for property ID {property_id}",
                    "error": str(e),
                }
            )
        return None

    def _deduplicate_dimensions(self, dimensions: List[Dimension]) -> List[Dimension]:
        """
        Deduplicate a list of Dimension objects using their name as a unique key.
        """
        seen = set()
        deduped = []
        for d in dimensions:
            if d.name not in seen:
                seen.add(d.name)
                deduped.append(d)
        return deduped

    @backoff.on_exception(
        backoff.expo, Exception, max_time=60, max_tries=3, giveup=give_up
    )
    @cached(ttl=300, cache=Cache.MEMORY)  # Cache results for 5 minutes
    async def _decorated_query_from_parts(
        self,
        metrics: List[Metric],
        dimensions: List[Dimension],
        date_ranges: List[DateRange],
        dimension_filter: Optional[FilterExpression],
        metric_filter: Optional[FilterExpression],
        order_bys: Optional[List[OrderBy]],
        limit: Optional[int],
        offset: Optional[int],
        property_id: str,
        include_totals: bool = True,
        **kwargs: str,
    ) -> Optional[RunReportResponse]:
        report_response = None
        try:
            deduplicated_dimensions = self._deduplicate_dimensions(dimensions)
            request = RunReportRequest(
                property=f"properties/{property_id}",
                date_ranges=date_ranges,
                dimensions=deduplicated_dimensions,
                metrics=metrics,
                metric_filter=metric_filter,
                dimension_filter=dimension_filter,
                order_bys=order_bys,
                limit=limit,
                offset=offset,
                keep_empty_rows=True,
                metric_aggregations=(
                    [MetricAggregation.TOTAL] if include_totals else None
                ),
            )
            report_response = await asyncio.wait_for(
                self._client.run_report(request), timeout=REQUEST_TIMEOUT
            )
        except (TimeoutError, asyncio.exceptions.TimeoutError) as timeout_error:
            LOGGER.warning(
                {
                    "error": str(timeout_error),
                    "msg": "timeout_error_from_ga4_client",
                    "property_id": property_id,
                }
            )
            raise timeout_error
        except Exception as e:
            LOGGER.warning(
                {
                    "msg": "failed_to_run_report",
                    "property_id": property_id,
                    "error": str(e),
                }
            )
            raise e

        return report_response

    async def _query(
        self,
        metrics: List[Metric],
        dimensions: List[Dimension],
        date_ranges: List[DateRange],
        dimension_filter: Optional[FilterExpression],
        metric_filter: Optional[FilterExpression],
        order_bys: Optional[List[OrderBy]],
        limit: Optional[int],
        offset: Optional[int],
        property_id: str,
        include_totals: bool = True,
        **kwargs: str,
    ) -> Optional[RunReportResponse]:
        # Use the new deduplication method instead of set() to avoid the unhashable error.
        deduplicated_dimensions = self._deduplicate_dimensions(dimensions)

        try:
            request = RunReportRequest(
                property=f"properties/{property_id}",
                date_ranges=date_ranges,
                dimensions=deduplicated_dimensions,
                metrics=metrics,
                metric_filter=metric_filter,
                dimension_filter=dimension_filter,
                order_bys=order_bys,
                limit=limit,
                offset=offset,
                keep_empty_rows=True,
                metric_aggregations=(
                    [MetricAggregation.TOTAL] if include_totals else None
                ),
            )
            report_response = await asyncio.wait_for(
                self._client.run_report(request), timeout=REQUEST_TIMEOUT
            )
        except (TimeoutError, asyncio.exceptions.TimeoutError) as timeout_error:
            LOGGER.warning(
                {
                    "error": str(timeout_error),
                    "msg": "timeout_error_from_ga4_client",
                    "property_id": property_id,
                }
            )
            raise timeout_error
        except Exception as e:
            LOGGER.warning(
                {
                    "msg": "failed_to_run_report",
                    "property_id": property_id,
                    "error": str(e),
                }
            )
            raise e

        return report_response

    @cached(ttl=300, cache=Cache.MEMORY)  # Cache results for 5 minutes
    async def _decorated_query(
        self,
        query_args: QueryArgs,
        property_id: str,
        **kwargs: str,
    ) -> Optional[ReportsClientQueryResult]:
        params = await GA4_PARSER.parse_query_args_to_request_params(
            query_args=query_args,
            property_id=property_id,
        )
        result = None
        try:
            result = await self._query(**params)

        except Exception as e:
            LOGGER.error(
                {
                    "msg": "ga4_query_failed",
                    "error": str(e),
                }
            )
            raise
        if result is None:
            return None

        generated_result_df = GA4_PARSER.parse_report_response_to_dataframe(
            report_response=result,
        )

        generated_totals_df = GA4_PARSER.parse_totals_to_dataframe(
            report_response=result,
        )

        return ReportsClientQueryResult(
            main_result=generated_result_df, totals_result=generated_totals_df
        )

    async def query(
        self,
        query_args: QueryArgs,
        property_id: str,
        **kwargs: str,
    ) -> Optional[ReportsClientQueryResult]:
        return await self._decorated_query(
            query_args=query_args, property_id=property_id, **kwargs
        )

    # Function to get the top N values for a given dimension.
    # Only return something for string dimensions.
    @cached(
        ttl=3600, cache=Cache.MEMORY, skip_cache_func=lambda x: x is None
    )  # Cache results for 1 hour
    async def _decorated_get_dimension_values(
        self, dimension: DimensionProto, top_n: int, property_id: str, **kwargs: str
    ) -> Optional[List[str]]:
        LOGGER.info(
            {
                "msg": "get_dimension_values",
                "dimension_metadata_name": dimension.name,
                "top_n": top_n,
            }
        )

        if COHORT_CATEGORY in dimension.name.lower():
            LOGGER.info(
                {
                    "msg": "cohort_dimension",
                }
            )
            return None

        # Check if the dimension is in COMMON_DIMENSIONS
        if COMMON_DIMENSIONS is not None:
            for common_dimension in COMMON_DIMENSIONS:
                if (
                    common_dimension.name == dimension.name
                    and len(common_dimension.top_n_values) >= top_n
                ):
                    LOGGER.info(
                        {
                            "msg": "common_dimension",
                            "dimension_metadata_name": dimension.name,
                        }
                    )
                    return common_dimension.top_n_values[:top_n]

        # Get the last year of data.
        date_ranges = [DateRange(start_date="365daysAgo", end_date="yesterday")]

        ga4_dimension = await self.get_ga4_dimension_from_name(
            dimension_name=dimension.name,
            property_id=property_id,
        )

        if ga4_dimension is None:
            LOGGER.error(
                {
                    "msg": "failed_to_get_ga4_dimension",
                    "dimension_metadata_name": dimension.name,
                }
            )
            return None

        response: Optional[RunReportResponse] = None

        try:
            response = await self._query(
                metrics=[SESSIONS_METRIC],
                dimensions=[ga4_dimension],
                date_ranges=date_ranges,
                dimension_filter=None,
                metric_filter=None,
                order_bys=[ORDER_BY_SESSIONS],
                offset=0,
                limit=top_n,
                property_id=property_id,
            )

            LOGGER.info(
                {
                    "msg": "request_suceessful_for_sessions",
                    "dimension": dimension.name,
                }
            )

        except ResourceExhausted as resource_exhausted:
            LOGGER.info(
                {
                    "msg": "resource_exhausted",
                    "dimension": dimension.name,
                    "error": str(resource_exhausted),
                }
            )
            return None

        except Exception as e:
            LOGGER.info(
                {
                    "msg": "get_top_n_values_for_dimension_failed_for_sessions",
                    "dimension": dimension.name,
                    "error": str(e),
                }
            )
            try:
                response = await self._query(
                    metrics=[],
                    dimensions=[ga4_dimension],
                    date_ranges=date_ranges,
                    dimension_filter=None,
                    metric_filter=None,
                    order_bys=None,
                    offset=0,
                    limit=top_n,
                    property_id=property_id,
                )

                LOGGER.info(
                    {
                        "msg": "request_suceessful",
                        "dimension": dimension.name,
                    }
                )
            except Exception as e:
                LOGGER.info(
                    {
                        "msg": "get_top_n_values_for_dimension_failed",
                        "dimension": dimension.name,
                        "error": str(e),
                    }
                )
                return None

        if response is None:
            LOGGER.info(
                {
                    "msg": "get_top_n_values_for_dimension_failed",
                    "dimension": dimension.name,
                }
            )
            return None

        values = []
        for row in response.rows:
            values.append(row.dimension_values[0].value)
        return values

    async def get_dimension_values(
        self, dimension: DimensionProto, top_n: int, property_id: str, **kwargs: str
    ) -> Optional[List[str]]:
        return await self._decorated_get_dimension_values(
            dimension=dimension, top_n=top_n, property_id=property_id, **kwargs
        )

    # Function to check if metric is collecting data.
    @cached(
        ttl=3600, cache=Cache.MEMORY, skip_cache_func=lambda x: x is None
    )  # Cache results for 1 hour
    async def _decorated_is_metric_empty(
        self, metric: Metric, property_id: str, **kwargs: str
    ) -> Optional[bool]:
        LOGGER.info(
            {
                "msg": "is_metric_empty",
                "metricn_metadata_name": metric.name,
            }
        )

        # Get the last year of data.
        date_ranges = [DateRange(start_date="365daysAgo", end_date="yesterday")]

        ga4_metric = await self.get_ga4_metric_from_name(
            metric_name=metric.name,
            property_id=property_id,
        )
        if ga4_metric is None:
            LOGGER.error(
                {
                    "msg": "failed_to_get_metric",
                    "metric_metadata_name": metric.name,
                }
            )
            return None

        try:
            response = await self._query(
                metrics=[ga4_metric],
                dimensions=[],
                date_ranges=date_ranges,
                dimension_filter=None,
                metric_filter=None,
                order_bys=None,
                offset=0,
                limit=1,
                property_id=property_id,
            )

            LOGGER.info(
                {
                    "msg": "request_suceessful",
                    "dimension": metric.api_name,
                }
            )

        except ResourceExhausted as resource_exhausted:
            LOGGER.info(
                {
                    "msg": "resource_exhausted",
                    "metric": metric.name,
                    "error": str(resource_exhausted),
                }
            )
            return None

        except Exception as e:
            LOGGER.info(
                {
                    "msg": "get_value_for_metric_failed",
                    "metric": metric.name,
                    "error": str(e),
                }
            )
            return None

        if response is None:
            LOGGER.info(
                {
                    "msg": "get_value_for_metric_failed",
                    "metric": metric.name,
                }
            )
            return None

        if len(response.rows) == 0:
            LOGGER.info(
                {
                    "msg": "metric_is_empty",
                    "metric": metric.name,
                }
            )
            return True
        return False

    async def is_metric_empty(
        self, metric: Metric, property_id: str, **kwargs: str
    ) -> Optional[bool]:
        return await self._decorated_is_metric_empty(
            metric=metric, property_id=property_id, **kwargs
        )

    @cached(
        ttl=3600, cache=Cache.MEMORY, skip_cache_func=lambda x: x is None
    )  # Cache results for 1 hour
    async def _decorated_get_metadata(
        self, property_id: str, **kwargs: str
    ) -> Optional[Metadata]:
        metadata_response = None
        try:
            request = GetMetadataRequest(name=f"properties/{property_id}/metadata")
            metadata_response = await self._client.get_metadata(request)
        except Exception as e:
            LOGGER.error(
                {
                    "msg": "failed_to_get_metadata",
                    "error": e,
                }
            )
            return None

        return metadata_response

    async def get_metadata(self, property_id: str, **kwargs: str) -> Optional[Metadata]:
        return await self._decorated_get_metadata(property_id=property_id, **kwargs)

    @cached(
        ttl=3600, cache=Cache.MEMORY, skip_cache_func=lambda x: x is None
    )  # Cache results for 1 hour
    async def _decorated_get_dimension_from_name(
        self, dimension_name: str, property_id: str, **kwargs: str
    ) -> Optional[DimensionProto]:
        LOGGER.info(
            {
                "msg": "getting_dimension_from_name",
                "dimension_name": dimension_name,
            }
        )

        def _get_dimension_from_metadata(
            dimension_metadata: DimensionMetadata,
        ) -> DimensionProto:
            """
            Converts a GA4 DimensionMetadata object into a Semantic layer Dimension object.

            Args:
                dimension_metadata (DimensionMetadata): The GA4 DimensionMetadata object.

            Returns:
                DimensionProto: The converted Semantic layer Dimension object.
            """
            dimension = DimensionProto()
            dimension.name = dimension_metadata.api_name
            dimension.description = dimension_metadata.description
            dimension.display_name = dimension_metadata.ui_name

            return dimension

        metadata_response: Optional[Metadata] = await self.get_metadata(
            property_id=property_id
        )

        if metadata_response is None:
            LOGGER.error(
                {
                    "msg": "failed_to_get_ga4_metric_from_name",
                }
            )
            return None

        for dimension_metadata in metadata_response.dimensions:
            if dimension_metadata.api_name == dimension_name:
                return _get_dimension_from_metadata(dimension_metadata)
        return None

    async def get_dimension_from_name(
        self, dimension_name: str, property_id: str, **kwargs: str
    ) -> Optional[DimensionProto]:
        return await self._decorated_get_dimension_from_name(
            dimension_name=dimension_name, property_id=property_id, **kwargs
        )

    @cached(
        ttl=3600, cache=Cache.MEMORY, skip_cache_func=lambda x: x is None
    )  # Cache results for 1 hour
    async def _decorated_get_metric_from_name(
        self, metric_name: str, property_id: str, **kwargs: str
    ) -> Optional[MetricProto]:
        LOGGER.info(
            {
                "msg": "getting_metric_from_name",
                "metric_name": metric_name,
            }
        )

        def _get_metric_from_metadata(
            metric_metadata: MetricMetadata,
        ) -> MetricProto:
            metric = MetricProto()
            metric.name = metric_metadata.api_name
            metric.description = metric_metadata.description
            metric.display_name = metric_metadata.ui_name
            metric.is_numeric = True

            if metric_metadata.type_ is not None:
                if metric_metadata.type_ == MetricType.TYPE_INTEGER:
                    metric.value_type = MetricValueType.METRIC_VALUE_TYPE_INTEGER
                elif metric_metadata.type_ == MetricType.TYPE_FLOAT:
                    metric.value_type = MetricValueType.METRIC_VALUE_TYPE_FLOAT
                elif metric_metadata.type_ == MetricType.TYPE_SECONDS:
                    metric.value_type = MetricValueType.METRIC_VALUE_TYPE_SECONDS
                elif metric_metadata.type_ == MetricType.TYPE_MILLISECONDS:
                    metric.value_type = MetricValueType.METRIC_VALUE_TYPE_MILLISECONDS
                elif metric_metadata.type_ == MetricType.TYPE_MINUTES:
                    metric.value_type = MetricValueType.METRIC_VALUE_TYPE_MINUTES
                elif metric_metadata.type_ == MetricType.TYPE_HOURS:
                    metric.value_type = MetricValueType.METRIC_VALUE_TYPE_HOURS
                elif metric_metadata.type_ == MetricType.TYPE_STANDARD:
                    metric.value_type = MetricValueType.METRIC_VALUE_TYPE_STANDARD
                elif metric_metadata.type_ == MetricType.TYPE_CURRENCY:
                    metric.value_type = MetricValueType.METRIC_VALUE_TYPE_CURRENCY
                elif metric_metadata.type_ == MetricType.TYPE_FEET:
                    metric.value_type = MetricValueType.METRIC_VALUE_TYPE_FEET
                elif metric_metadata.type_ == MetricType.TYPE_MILES:
                    metric.value_type = MetricValueType.METRIC_VALUE_TYPE_MILES
                elif metric_metadata.type_ == MetricType.TYPE_METERS:
                    metric.value_type = MetricValueType.METRIC_VALUE_TYPE_METERS
                elif metric_metadata.type_ == MetricType.TYPE_KILOMETERS:
                    metric.value_type = MetricValueType.METRIC_VALUE_TYPE_KILOMETERS
                else:
                    metric.value_type = MetricValueType.METRIC_VALUE_TYPE_UNKNOWN

            return metric

        metadata_response: Optional[Metadata] = await self.get_metadata(
            property_id=property_id
        )

        if metadata_response is None:
            LOGGER.error(
                {
                    "msg": "failed_to_get_metric_from_name",
                }
            )
            return None

        for metric_metadata in metadata_response.metrics:
            if metric_metadata.api_name == metric_name:
                return _get_metric_from_metadata(metric_metadata)
        return None

    async def get_metric_from_name(
        self, metric_name: str, property_id: str, **kwargs: str
    ) -> Optional[MetricProto]:
        return await self._decorated_get_metric_from_name(
            metric_name=metric_name, property_id=property_id, **kwargs
        )

    @cached(
        ttl=3600, cache=Cache.MEMORY, skip_cache_func=lambda x: x is None
    )  # Cache results for 1 hour
    async def _decorated_get_ga4_dimension_from_name(
        self, dimension_name: str, property_id: str, **kwargs: str
    ) -> Optional[Dimension]:
        LOGGER.info(
            {
                "msg": "getting_dimension_from_name",
                "dimension_name": dimension_name,
            }
        )

        metadata_response: Optional[Metadata] = await self.get_metadata(
            property_id=property_id
        )

        if metadata_response is None:
            LOGGER.error(
                {
                    "msg": "failed_to_get_ga4_metric_from_name",
                }
            )
            return None

        for dimension in metadata_response.dimensions:
            if dimension.api_name == dimension_name:
                return Dimension(name=dimension.api_name)
        return None

    async def get_ga4_dimension_from_name(
        self, dimension_name: str, property_id: str, **kwargs: str
    ) -> Optional[Dimension]:
        return await self._decorated_get_ga4_dimension_from_name(
            dimension_name=dimension_name, property_id=property_id, **kwargs
        )

    @cached(
        ttl=3600, cache=Cache.MEMORY, skip_cache_func=lambda x: x is None
    )  # Cache results for 1 hour
    async def _decorated_get_ga4_metric_from_name(
        self, metric_name: str, property_id: str, **kwargs: str
    ) -> Optional[Metric]:
        LOGGER.info(
            {
                "msg": "getting_metric_from_name",
                "metric_name": metric_name,
            }
        )

        metadata_response: Optional[Metadata] = await self.get_metadata(
            property_id=property_id
        )

        if metadata_response is None:
            LOGGER.error(
                {
                    "msg": "failed_to_get_ga4_metric_from_name",
                }
            )
            return None

        for metric in metadata_response.metrics:
            if metric.api_name == metric_name:
                return Metric(name=metric.api_name, expression=metric.expression)
        return None

    async def get_ga4_metric_from_name(
        self, metric_name: str, property_id: str, **kwargs: str
    ) -> Optional[Metric]:
        return await self._decorated_get_ga4_metric_from_name(
            metric_name=metric_name, property_id=property_id, **kwargs
        )

    @cached(
        ttl=3600, cache=Cache.MEMORY, skip_cache_func=lambda x: x is None
    )  # Cache results for 1 hour
    async def _decorated_list_dimensions(
        self, property_id: str, **kwargs: str
    ) -> Optional[List[DimensionProto]]:
        LOGGER.info(
            {
                "msg": "listing_dimensions",
            }
        )

        metadata_response: Optional[Metadata] = await self.get_metadata(
            property_id=property_id
        )

        if metadata_response is None:
            LOGGER.error(
                {
                    "msg": "failed_to_list_dimensions",
                }
            )
            return None

        dimensions_list: List[Optional[DimensionProto]] = await asyncio.gather(
            *[
                self.get_dimension_from_name(
                    dimension_name=dimension_metadata.api_name,
                    property_id=property_id,
                )
                for dimension_metadata in metadata_response.dimensions
            ]
        )

        # Filter out None values
        filtered_dimensions_list = list(filter(None, dimensions_list))

        return filtered_dimensions_list

    async def list_dimensions(
        self, property_id: str, **kwargs: str
    ) -> Optional[List[DimensionProto]]:
        return await self._decorated_list_dimensions(property_id=property_id, **kwargs)

    @cached(
        ttl=3600, cache=Cache.MEMORY, skip_cache_func=lambda x: x is None
    )  # Cache results for 1 hour
    async def _decorated_list_metrics(
        self, property_id: str, **kwargs: str
    ) -> Optional[List[MetricProto]]:
        LOGGER.info(
            {
                "msg": "listing_metrics",
            }
        )

        metadata_response: Optional[Metadata] = await self.get_metadata(
            property_id=property_id
        )

        if metadata_response is None:
            LOGGER.error(
                {
                    "msg": "failed_to_list_metrics",
                    "property_id": property_id,
                }
            )
            return None

        metrics_list: List[Optional[MetricProto]] = await asyncio.gather(
            *[
                self.get_metric_from_name(
                    metric_name=metric_metadata.api_name, property_id=property_id
                )
                for metric_metadata in metadata_response.metrics
            ]
        )

        # Filter out None values
        filtered_metrics_list = list(filter(None, metrics_list))

        return filtered_metrics_list

    async def list_metrics(
        self, property_id: str, **kwargs: str
    ) -> Optional[List[MetricProto]]:
        return await self._decorated_list_metrics(property_id=property_id, **kwargs)

    @cached(
        ttl=3600, cache=Cache.MEMORY, skip_cache_func=lambda x: x is None
    )  # Cache results for 1 hour
    async def _decorated_get_used_metrics(
        self, property_id: str, **kwargs: str
    ) -> Optional[List[str]]:
        """
        Asynchronously retrieves a list of used metrics from a Google Analytics 4 property.

        Args:
            property_id (str): The Google Analytics 4 property identifier.

        Returns:
            Optional[List[str]]: A list of used metrics api names any exist, None otherwise.
        """
        LOGGER.info(
            {
                "msg": "getting_used_metrics",
                "property_id": property_id,
            }
        )
        metrics_list: Optional[List[MetricProto]] = await self.list_metrics(
            property_id=property_id, **kwargs
        )
        if metrics_list is None:
            LOGGER.info(
                {
                    "msg": "no_metrics_metadata_found",
                    "property_id": property_id,
                }
            )
            return None

        tasks = [
            self.is_metric_empty(
                metric=Metric(name=metric.name),
                property_id=property_id,
                **kwargs,
            )
            for metric in metrics_list
        ]

        responses = await asyncio.gather(*tasks)

        filtered_metrics_list = []

        for index, response in enumerate(responses):
            if not response:
                LOGGER.info(
                    {
                        "msg": "metrics_values_found",
                        "property_id": property_id,
                        "metric_name": metrics_list[index].name,
                    }
                )
                filtered_metrics_list.append(metrics_list[index].name)

        return filtered_metrics_list

    async def get_used_metrics(
        self, property_id: str, **kwargs: str
    ) -> Optional[List[str]]:
        return await self._decorated_get_used_metrics(property_id=property_id, **kwargs)

    @cached(
        ttl=3600, cache=Cache.MEMORY, skip_cache_func=lambda x: x is None
    )  # Cache results for 1 hour
    async def _decorated_get_used_dimensions(
        self, property_id: str, **kwargs: str
    ) -> Optional[List[str]]:
        """
        Asynchronously retrieves a list of used dimensions from a Google Analytics 4 property.

        Args:
            property_id (str): The Google Analytics 4 property identifier.

        Returns:
            Optional[List[str]]: A list of used dimensions' display names if any exist, None otherwise.
        """
        LOGGER.info(
            {
                "msg": "getting_used_dimensions",
                "property_id": property_id,
            }
        )
        all_dimension_list = await self.list_dimensions(
            property_id=property_id, **kwargs
        )
        if all_dimension_list is None:
            LOGGER.info(
                {
                    "msg": "no_dimensions_metadata_found",
                    "property_id": property_id,
                }
            )
            return None

        tasks = [
            self.get_dimension_values(
                dimension=dimension, top_n=5, property_id=property_id, **kwargs
            )
            for dimension in all_dimension_list
        ]

        dimensions_top_n = await asyncio.gather(*tasks)

        filtered_dimension_list = []
        for index, dimension_top_n in enumerate(dimensions_top_n):
            if dimension_top_n is None:
                continue
            if EMPTY_STRING in dimension_top_n:
                dimension_top_n.remove(EMPTY_STRING)
            if NOT_SET_VALUE in dimension_top_n:
                dimension_top_n.remove(NOT_SET_VALUE)
            if len(dimension_top_n) > 0:
                LOGGER.info(
                    {
                        "msg": "dimensions_values_found",
                        "property_id": property_id,
                        "dimension_name": all_dimension_list[index].name,
                    }
                )
                filtered_dimension_list.append(all_dimension_list[index].name)

        if len(filtered_dimension_list) == 0:
            LOGGER.info(
                {
                    "msg": "no_dimensions_with_top_n_found",
                    "property_id": property_id,
                }
            )
            return None

        return filtered_dimension_list

    async def get_used_dimensions(
        self, property_id: str, **kwargs: str
    ) -> Optional[List[str]]:
        return await self._decorated_get_used_dimensions(
            property_id=property_id, **kwargs
        )

    @backoff.on_exception(
        backoff.expo, Exception, max_time=60, max_tries=3, giveup=give_up
    )
    @cached(
        ttl=300, cache=Cache.MEMORY, skip_cache_func=lambda x: x is None
    )  # Cache results for 5 minutes
    async def _decorated_check_compatibility(
        self,
        property_id: str,
        metrics: Optional[List[Metric]] = None,
        dimensions: Optional[List[Dimension]] = None,
        dimension_filter: Optional[FilterExpression] = None,
        metric_filter: Optional[FilterExpression] = None,
        **kwargs: str,
    ) -> Optional[CheckCompatibilityResponse]:
        try:
            property = f"properties/{property_id}"
            # Initialize request argument(s)
            request = CheckCompatibilityRequest(
                property=property,
                metrics=metrics,
                dimensions=dimensions,
                dimension_filter=dimension_filter,
                metric_filter=metric_filter,
                compatibility_filter=Compatibility.COMPATIBLE,
            )
            response = await self._client.check_compatibility(request=request)
            return response
        except Exception as e:
            LOGGER.error(
                {
                    "msg": "check_compatibility_failed",
                    "error": str(e),
                }
            )
            raise e

    async def check_compatibility(
        self,
        property_id: str,
        metrics: Optional[List[Metric]] = None,
        dimensions: Optional[List[Dimension]] = None,
        dimension_filter: Optional[FilterExpression] = None,
        metric_filter: Optional[FilterExpression] = None,
        **kwargs: str,
    ) -> Optional[CheckCompatibilityResponse]:
        return await self._decorated_check_compatibility(
            property_id=property_id,
            metrics=metrics,
            dimensions=dimensions,
            dimension_filter=dimension_filter,
            metric_filter=metric_filter,
            **kwargs,
        )
