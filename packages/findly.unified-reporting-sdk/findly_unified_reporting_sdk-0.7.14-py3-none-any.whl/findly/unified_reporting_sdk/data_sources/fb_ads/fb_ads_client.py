import backoff
import logging
import pandas as pd
from typing import List, Dict, Optional, Tuple, Union
from aiocache import cached, Cache

from facebook_business.api import FacebookAdsApi, FacebookSession
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.adobjects.user import User
from facebook_business.adobjects.business import Business

from findly.unified_reporting_sdk.data_sources.common.entities import (
    ReportsClientQueryResult,
)
from findly.unified_reporting_sdk.data_sources.common.reports_client import (
    ReportsClient,
)
from findly.unified_reporting_sdk.data_sources.fb_ads.fb_ads_query_args_parser import (
    FbAdsQueryArgsParser,
    DATE,
    YEARMONTH,
)
from findly.unified_reporting_sdk.protos.findly_semantic_layer_pb2 import (
    DimensionType,
    Dimension,
    Metric,
    QueryArgs,
)
from itertools import islice
import json
from facebook_business.exceptions import (
    FacebookUnavailablePropertyException,
)

LOGGER = logging.getLogger(__name__)

logging.getLogger("backoff").setLevel(logging.WARNING)

REPORT_TIMEOUT = 30  # Maximum timeout for the report to complete

ATTRIBUTION_SETTING = "attribution_setting"

FB_PARSER = FbAdsQueryArgsParser.default()

DEFAULT_PAGE_SIZE_FOR_FB_ADS_PAGINATED_CALL = 1000
DEFAULT_LIMIT_FOR_ADS_INSIGHTS_CURSOR = 1000


class FbAdsClient(ReportsClient):
    """
    Attributes:
        _api(FacebookAdsApi)
    """

    _api: FacebookAdsApi

    def __init__(
        self,
        token: str,
        client_id: str,
        client_secret: str,
    ):
        """
        Initialize the FbAdsClient with an access token.

        Args:
            token (str): The access token for the Facebook Ads API.
        """
        api_version = None
        proxies = None
        timeout = None
        debug = False

        session = FacebookSession(client_id, client_secret, token, proxies, timeout)
        self._api = FacebookAdsApi(session, api_version, enable_debug_logger=debug)

    async def list_all_ad_accounts(self, **kwargs: str) -> Optional[List[str]]:
        """
        List all ad accounts for the user.

        Returns:
            List[str]: A list of AdAccount Ids.
        """
        try:
            # fbid='me' is used to refer to the currently authenticated user.
            client = User(fbid="me", api=self._api)
            ad_accounts = client.get_ad_accounts()

            # Now get the ad_accont_ids
            ad_account_ids = [account["id"] for account in ad_accounts]

            LOGGER.info(
                {
                    "msg": "user_ad_accounts",
                    "ids": ad_account_ids,
                }
            )

            # Fetch all businesses associated with the user
            business_fields = ["id", "name"]
            businesses = client.get_businesses(fields=business_fields)

            # Define fields to fetch for ad accounts
            ad_account_fields = ["id", "name"]

            # For each business, fetch and print all ad accounts
            for business in businesses:
                business_id = business["id"]
                business_name = business["name"]

                # Get the business object
                business_entity = Business(fbid=business_id, api=self._api)

                # Fetch all owned ad accounts for the business
                # These are ad accounts that the business has created and has full control over.
                owned_ad_accounts = business_entity.get_owned_ad_accounts(
                    fields=ad_account_fields
                )
                owned_ad_accounts_ids = [
                    account[AdAccount.Field.id] for account in owned_ad_accounts
                ]
                LOGGER.info(
                    {
                        "msg": "Owned ad accounts",
                        "business_name": business_name,
                        "business_id": business_id,
                        "ids": owned_ad_accounts_ids,
                    }
                )
                ad_account_ids.extend(owned_ad_accounts_ids)

                # Fetch all client ad accounts for the business
                #  This method retrieves ad accounts that are managed by the business entity but are owned by another entity (client).
                # In this scenario, the business entity typically has been granted access to manage these accounts on behalf of the client.
                client_ad_accounts = business_entity.get_client_ad_accounts(
                    fields=ad_account_fields
                )
                client_ad_accounts_ids = [
                    account[AdAccount.Field.id] for account in client_ad_accounts
                ]
                LOGGER.info(
                    {
                        "msg": "Client ad accounts",
                        "business_name": business_name,
                        "business_id": business_id,
                        "ids": client_ad_accounts_ids,
                    }
                )
                ad_account_ids.extend(client_ad_accounts_ids)
            return ad_account_ids

        except Exception as e:
            LOGGER.error(
                {
                    "msg": "Error listing ad accounts",
                    "error": str(e),
                }
            )
            return None

    async def list_property_ids(self, **kwargs: str) -> Optional[List[str]]:
        return await self.list_all_ad_accounts()

    @backoff.on_exception(backoff.expo, Exception, max_time=60, max_tries=3)
    @cached(ttl=300, cache=Cache.MEMORY)  # Cache results for 5 minutes
    async def _decorated_query_from_parts(
        self,
        ad_account_id: str,
        metrics_names: List[str],
        dimensions: Optional[List[Dimension]] = None,
        time_ranges: Optional[
            List[Dict[str, str]]
        ] = None,  # If not specified, defaults to last 30 days
        sort: Optional[List[str]] = None,
        filtering: Optional[List[Dict[str, str]]] = None,
        limit: Union[int, str] = DEFAULT_LIMIT_FOR_ADS_INSIGHTS_CURSOR,
        level: AdsInsights.Level = AdsInsights.Level.account,
        page_size: int = DEFAULT_PAGE_SIZE_FOR_FB_ADS_PAGINATED_CALL,
        **kwargs: str,
    ) -> Optional[Tuple[List[AdsInsights], Optional[Dict]]]:
        """
        Query the Facebook Ads API for insights.

        Args:
            ad_account_id (str): The ad account ID.
            metrics_names (List[str]): The Metric fields to include in the response.
            dimensions (Optional[List[Dimension]]): The dimensions that can be fields, breakdowns, action breakdowns...
            time_ranges (Optional[List[Dict[str, str]]]): The time ranges to apply.
            sort (Optional[List[str]]): The sort order to apply.
            filtering (Optional[List[Dict[str, str]]): The filters to apply.
            level (AdsInsights.Level): The level of insights to return.

        Returns:
            Optional[Tuple[List[AdsInsights], Optional[Dict]]]: A tuple of AdsInsights List and Summary, or None if an error occurred.
        """
        try:
            limit = int(limit)
        except ValueError as e:
            LOGGER.error(
                {
                    "msg": "fb_ads_query_failed",
                    "error": str(e),
                }
            )
            return None
        except TypeError as e:
            LOGGER.error(
                {
                    "msg": "fb_ads_query_failed",
                    "error": str(e),
                }
            )
            return None

        fields = list(metrics_names)
        params = {"level": level, "default_summary": "true"}
        if dimensions:
            fields_dimensions = [
                dimension.name
                for dimension in dimensions
                if dimension is not None
                and dimension.type == DimensionType.FB_ADS_FIELD
            ]
            fields.extend(fields_dimensions)
            # Following the Facebook Ads API documentation,
            # Note: The attribution_setting field only returns values when use_unified_attribution_setting is set to true.
            # https://developers.facebook.com/docs/marketing-api/reference/ads-insights/
            if ATTRIBUTION_SETTING in fields_dimensions:
                params["use_unified_attribution_setting"] = "true"

            params["breakdowns"] = [
                dimension.name
                for dimension in dimensions
                if dimension is not None
                and dimension.type == DimensionType.FB_ADS_BREAKDOWN
            ]
            params["action_breakdowns"] = [
                dimension.name
                for dimension in dimensions
                if dimension is not None
                and dimension.type == DimensionType.FB_ADS_ACTION_BREAKDOWN
            ]

            if DATE in [dimension.name for dimension in dimensions]:
                params["time_increment"] = "1"
            elif YEARMONTH in [dimension.name for dimension in dimensions]:
                params["time_increment"] = "monthly"

        # in Fb ads, multiple time_ranges and time_increment don't work together
        # So if we have multiple time_ranges, we give preference to time_ranges
        # if we have a single one, we use singular date range and time_increment
        if time_ranges:
            if len(time_ranges) > 1:
                params["time_ranges"] = time_ranges
            else:
                params["time_range"] = time_ranges[0]
                # TODO (jutogashi): check if we want to add this back
                # if time_increment:
                #     params["time_increment"] = time_increment
        if sort:
            params["sort"] = sort
        if filtering:
            params["filtering"] = filtering

        params["limit"] = page_size

        try:
            insights_cursor = AdAccount(fbid=ad_account_id, api=self._api).get_insights(
                fields=fields,
                params=params,
            )
            summary: Optional[Dict] = None
            try:
                summary_text = insights_cursor.summary()
                # the string has <Summary> before the JSON string
                # This splits on "> "and takes the second part, which is the JSON string
                summary_json = summary_text.split("> ")[1]
                summary = json.loads(summary_json)
            except FacebookUnavailablePropertyException as e:
                LOGGER.info(
                    {
                        "msg": "error_getting_summary",
                        "error": str(e),
                    }
                )
            insights_cursor_slice = islice(insights_cursor, limit)
            insights = list(insights_cursor_slice)

            return insights, summary

        except Exception as e:
            LOGGER.info(
                {
                    "msg": "Error querying Facebook Ads API",
                    "ad_account_id": ad_account_id,
                    "error": str(e),
                }
            )
            raise e

    @cached(ttl=300, cache=Cache.MEMORY)  # Cache results for 5 minutes
    async def _decorated_query(
        self,
        query_args: QueryArgs,
        property_id: str,
        **kwargs: str,
    ) -> Optional[ReportsClientQueryResult]:
        params = await FB_PARSER.parse_query_args_to_request_params(
            query_args=query_args,
            property_id=property_id,
        )
        insights = None
        try:
            insights, summary = await self._decorated_query_from_parts(**params)

        except Exception as e:
            LOGGER.error(
                {
                    "msg": "fb_ads_query_failed",
                    "error": str(e),
                }
            )
            raise e

        if insights is None:
            return None

        generated_result_df = await FB_PARSER.parse_report_response_to_dataframe(
            report_response=insights,
            query_args=query_args,
        )

        generated_totals_df = FB_PARSER.parse_totals_to_dataframe(
            summary=summary,
            query_args=query_args,
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
            query_args=query_args,
            property_id=property_id,
            **kwargs,
        )

    @cached(
        ttl=3600, cache=Cache.MEMORY, skip_cache_func=lambda x: x is None
    )  # Cache results for 1 hour
    async def _decorated_get_dimension_values(
        self,
        dimension: Dimension,
        top_n: int,
        property_id: str,
        level: AdsInsights.Level = AdsInsights.Level.account,
        **kwargs: str,
    ) -> Optional[List[str]]:
        """
        Get the top N values for a specified dimension from the Facebook Ads API.

        This method queries the Facebook Ads API for insights, with the specified dimension.
        It then returns the top N values for the dimension.

        Args:
            dimension (Dimension): the dimension.
            top_n (int): The number of top values to return.
            property_id (str): The ad account ID.
            level (AdsInsights.Level): TODO describe level,

        Returns:
            Optional[List[str]]: A list of the top N values for the dimension, or None if an error occurred.
        """
        LOGGER.info(
            {
                "msg": "get_fb_ads_dimension_values",
                "dimension_name": dimension.name,
                "dimension_type": dimension.type,
                "top_n": top_n,
                "level": level,
            }
        )

        try:
            if dimension.type == DimensionType.FB_ADS_BREAKDOWN:
                response = await self._decorated_query_from_parts(
                    ad_account_id=property_id,
                    metrics_names=["impressions"],
                    dimensions=[dimension],
                    sort=["impressions_descending"],
                    level=level,
                )
                if response is None:
                    LOGGER.info(
                        {
                            "msg": "no_response_for_query",
                            "dimension_metadata_name": dimension.name,
                            "dimension_type": dimension.type,
                            "top_n": top_n,
                        }
                    )
                    return None

                result = [insight[dimension.name] for insight in response[0][:top_n]]

            elif dimension.type == DimensionType.FB_ADS_ACTION_BREAKDOWN:
                response = await self._decorated_query_from_parts(
                    ad_account_id=property_id,
                    metrics_names=["actions"],
                    dimensions=[dimension],
                    level=level,
                )
                if response is None:
                    LOGGER.info(
                        {
                            "msg": "no_response_for_query",
                            "dimension_metadata_name": dimension.name,
                            "dimension_type": dimension.type,
                            "top_n": top_n,
                        }
                    )
                    return None
                response_list = response[0]
                actions_dict: Dict[str, int] = {}
                if len(response_list) != 1:
                    logging.warning(
                        {
                            "msg": "response_length_not_1_for_action_breakdown",
                            "dimension_metadata_name": dimension.name,
                            "response_length": len(response_list),
                        }
                    )
                    # If the response_list length is 0, return an empty list
                    # If the response_list length is > 1, return the top N values for the first element
                    # but keep a warning in the logs, so we know that something is wrong
                    if len(response_list) == 0:
                        return []
                for action in response_list[0]["actions"]:
                    if dimension.name in action:
                        if (
                            action[dimension.name] not in actions_dict
                            or int(action["value"])
                            > actions_dict[action[dimension.name]]
                        ):
                            actions_dict[action[dimension.name]] = int(action["value"])

                top_actions = sorted(
                    actions_dict.items(), key=lambda item: item[1], reverse=True
                )[:top_n]

                result = [action[0] for action in top_actions]

            elif dimension.type == DimensionType.FB_ADS_FIELD:
                response = await self._decorated_query_from_parts(
                    ad_account_id=property_id,
                    metrics_names=[],  # No metrics needed for this query
                    dimensions=[dimension],
                    sort=[f"{dimension.name}_descending"],
                    level=AdsInsights.Level.ad,
                )

                if response is None:
                    LOGGER.info(
                        {
                            "msg": "no_response_for_query",
                            "dimension_metadata_name": dimension.name,
                            "dimension_type": dimension.type,
                            "top_n": top_n,
                        }
                    )
                    return None

                result = [insight[dimension.name] for insight in response[0][:top_n]]
                result = list(set(result))  # Remove duplicates

            else:
                LOGGER.info(
                    {
                        "msg": "dimension_type_not_supported",
                        "dimension_metadata_name": dimension.name,
                        "top_n": top_n,
                    }
                )
                return None

            LOGGER.info(
                {
                    "msg": "get_fb_ads_dimension_values_successful",
                    "dimension_metadata_name": dimension.name,
                    "top_n": top_n,
                }
            )
            return result

        except Exception as e:
            LOGGER.info(
                {
                    "msg": "error_getting_fb_ads_dimension_values",
                    "dimension_metadata_name": dimension.name,
                    "top_n": top_n,
                    "error": str(e),
                }
            )
            return None

    async def get_dimension_values(
        self,
        dimension: Dimension,
        top_n: int,
        property_id: str,
        level: AdsInsights.Level = AdsInsights.Level.account,
        **kwargs: str,
    ) -> Optional[List[str]]:
        return await self._decorated_get_dimension_values(
            dimension=dimension,
            top_n=top_n,
            property_id=property_id,
            level=level,
            **kwargs,
        )

    async def list_metrics(
        self, property_id: str, **kwargs: str
    ) -> Optional[List[Metric]]:
        LOGGER.info(
            {
                "msg": "Getting metrics from json",
                "ad_account_id": property_id,
            }
        )
        try:
            metrics_list = FB_PARSER.parse_metrics()
            return metrics_list
        except Exception as e:
            LOGGER.error(f"An unexpected error occurred parsing Metrics: {e}")
        return None

    async def list_dimensions(
        self, property_id: str, **kwargs: str
    ) -> Optional[List[Dimension]]:
        LOGGER.info(
            {
                "msg": "Getting dimensions from json",
                "ad_account_id": property_id,
            }
        )
        try:
            dimensions_list = FB_PARSER.parse_dimensions()
            return dimensions_list
        except Exception as e:
            LOGGER.error(f"An unexpected error occurred parsing dimensions: {e}")
        return None

    async def get_metric_from_name(
        self, metric_name: str, property_id: str, **kwargs: str
    ) -> Optional[Metric]:
        fb_metrics_list: Optional[List[Metric]] = await self.list_metrics(
            property_id=property_id,
        )

        if fb_metrics_list is None:
            LOGGER.info(
                {
                    "msg": "no_fb_ads_metric_found",
                }
            )
            return None

        for metric in fb_metrics_list:
            if metric.name == metric_name:
                LOGGER.info(
                    {
                        "msg": "metric_found",
                        "metric": metric_name,
                    }
                )
                return metric

        return None

    async def get_dimension_from_name(
        self, dimension_name: str, property_id: str, **kwargs: str
    ) -> Optional[Dimension]:
        fb_dimensions_list: Optional[List[Dimension]] = await self.list_dimensions(
            property_id=property_id,
        )

        if fb_dimensions_list is None:
            LOGGER.info(
                {
                    "msg": "no_fb_ads_dimensions_found",
                }
            )
            return None

        for dimension in fb_dimensions_list:
            if dimension.name == dimension_name:
                LOGGER.info(
                    {
                        "msg": "dimension_found",
                        "dimension": dimension_name,
                    }
                )
                return dimension

        return None
