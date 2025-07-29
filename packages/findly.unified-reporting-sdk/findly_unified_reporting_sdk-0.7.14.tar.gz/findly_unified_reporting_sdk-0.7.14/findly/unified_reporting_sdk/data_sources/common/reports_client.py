from abc import ABC, abstractmethod
from typing import List, Optional

from findly.unified_reporting_sdk.data_sources.common.entities import (
    ReportsClientQueryResult,
)
from findly.unified_reporting_sdk.protos.findly_semantic_layer_pb2 import (
    Dimension,
    Metric,
    QueryArgs,
)


class ReportsClient(ABC):
    @abstractmethod
    async def list_property_ids(self, **kwargs: str) -> Optional[List[str]]:
        """
        List all property ids for the authenticated user.

        Returns:
            Optional[List[str]]: A list of property ids.
        """

    @abstractmethod
    async def query(
        self, query_args: QueryArgs, property_id: str, **kwargs: str
    ) -> Optional[ReportsClientQueryResult]:
        """
        Executes the integration API request based on the SQL query parts.

        Args:
            query_args (QueryArgs): The parts of the SQL query to execute.
            property_id (str): The property ID to execute the query for.

        Returns:
            Optional[ReportsClientQueryResult]: The query result, or None if the query failed.
        """
        pass

    @abstractmethod
    async def get_dimension_values(
        self, dimension: Dimension, top_n: int, property_id: str, **kwargs: str
    ) -> Optional[List[str]]:
        """
        Retrieves a sample of the top N values of a dimension.

        Args:
            dimension (Dimension): The dimension to retrieve the values for.
            top_n (int): The number of top values to retrieve.
            property_id (str): The property ID to retrieve the values for.

        Returns:
            Optional[List[str]]: A list of the top N dimension values, or None if the retrieval failed.
        """
        pass

    @abstractmethod
    async def list_dimensions(
        self, property_id: str, **kwargs: str
    ) -> Optional[List[Dimension]]:
        """
        Retrieves a list of all property dimensions from the API.

        Args:
            property_id (str): The property ID to retrieve the dimensions for.

        Returns:
            Optional[List[Dimension]]: A list of all dimensions, or None if the retrieval failed.
        """
        pass

    @abstractmethod
    async def list_metrics(
        self, property_id: str, **kwargs: str
    ) -> Optional[List[Metric]]:
        """
        Retrieves a list of all property metrics from the API.

        Args:
            property_id: The property ID to retrieve the metrics for.

        Returns:
            A list of all metrics, or None if the retrieval failed.
        """
        pass

    @abstractmethod
    async def get_dimension_from_name(
        self, dimension_name: str, property_id: str, **kwargs: str
    ) -> Optional[Dimension]:
        """
        Retrieves a dimension object by its name.

        Args:
            dimension_name (str): The name of the dimension to retrieve.
            property_id (str): The property ID to retrieve the dimension for.

        Returns:
            Optional[Dimension]: The dimension with the given name, or None if the dimension was not found.
        """
        pass

    @abstractmethod
    async def get_metric_from_name(
        self, metric_name: str, property_id: str, **kwargs: str
    ) -> Optional[Metric]:
        """
        Retrieves a metric object by its name.

        Args:
            metric_name (str): The name of the metric to retrieve.
            property_id (str): The property ID to retrieve the metric for.

        Returns:
            Optional[Metric]: The metric with the given name, or None if the metric was not found.
        """
        pass
