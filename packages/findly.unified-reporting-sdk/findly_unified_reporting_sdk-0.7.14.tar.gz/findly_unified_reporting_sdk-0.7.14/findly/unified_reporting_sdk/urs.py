from typing import List, Optional, Any

from findly.unified_reporting_sdk.data_sources.common.reports_client import (
    ReportsClient,
)
from findly.unified_reporting_sdk.data_sources.common.entities import (
    ReportsClientQueryResult,
)
from findly.unified_reporting_sdk.protos.findly_semantic_layer_pb2 import (
    Dimension,
    Metric,
    QueryArgs,
    DataSourceIntegration,
)
from findly.unified_reporting_sdk.data_sources.fb_ads.fb_ads_client import FbAdsClient
from findly.unified_reporting_sdk.data_sources.ga4.ga4_client import GA4Client


class Urs(ReportsClient):
    """
    Attributes:
        _client(ReportsClient)
    """

    _client: ReportsClient

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token: str,
        integration: DataSourceIntegration.ValueType,
    ):
        ConcreteClientClass = {  # noqa
            DataSourceIntegration.FB_ADS: FbAdsClient,
            DataSourceIntegration.GA4: GA4Client,
        }.get(integration)

        if ConcreteClientClass is None:
            raise ValueError("Integration not supported")

        self._client = ConcreteClientClass(
            token=token, client_id=client_id, client_secret=client_secret
        )

    async def query(
        self, query_args: QueryArgs, property_id: str, **kwargs: str
    ) -> Optional[ReportsClientQueryResult]:
        return await self._client.query(
            query_args=query_args, property_id=property_id, **kwargs
        )

    async def list_property_ids(self, **kwargs: str) -> Optional[List[str]]:
        return await self._client.list_property_ids(**kwargs)

    async def get_dimension_values(
        self, dimension: Dimension, top_n: int, property_id: str, **kwargs: str
    ) -> Optional[List[str]]:
        return await self._client.get_dimension_values(
            dimension=dimension, top_n=top_n, property_id=property_id, **kwargs
        )

    async def list_dimensions(
        self, property_id: str, **kwargs: str
    ) -> Optional[List[Dimension]]:
        return await self._client.list_dimensions(property_id=property_id, **kwargs)

    async def list_metrics(
        self, property_id: str, **kwargs: str
    ) -> Optional[List[Metric]]:
        return await self._client.list_metrics(property_id=property_id, **kwargs)

    async def get_dimension_from_name(
        self, dimension_name: str, property_id: str, **kwargs: str
    ) -> Optional[Dimension]:
        return await self._client.get_dimension_from_name(
            dimension_name=dimension_name, property_id=property_id, **kwargs
        )

    async def get_metric_from_name(
        self, metric_name: str, property_id: str, **kwargs: str
    ) -> Optional[Metric]:
        return await self._client.get_metric_from_name(
            metric_name=metric_name, property_id=property_id, **kwargs
        )

    def __getattr__(self, name: Any) -> Any:
        return getattr(self._client, name)
