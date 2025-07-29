from typing import Annotated
from uuid import UUID

from arthur_common.aggregations.aggregator import SketchAggregationFunction
from arthur_common.models.metrics import DatasetReference, SketchMetric
from arthur_common.models.schema_definitions import (
    DType,
    MetricColumnParameterAnnotation,
    MetricDatasetParameterAnnotation,
    ScalarType,
    ScopeSchemaTag,
)
from arthur_common.tools.duckdb_data_loader import escape_identifier, escape_str_literal
from duckdb import DuckDBPyConnection


class NumericSketchAggregationFunction(SketchAggregationFunction):
    METRIC_NAME = "numeric_sketch"

    @staticmethod
    def id() -> UUID:
        return UUID("00000000-0000-0000-0000-00000000000d")

    @staticmethod
    def display_name() -> str:
        return "Numeric Distribution"

    @staticmethod
    def description() -> str:
        return (
            "Metric that calculates a distribution (data sketch) on a numeric column."
        )

    def aggregate(
        self,
        ddb_conn: DuckDBPyConnection,
        dataset: Annotated[
            DatasetReference,
            MetricDatasetParameterAnnotation(
                friendly_name="Dataset",
                description="The dataset containing the numeric data.",
            ),
        ],
        timestamp_col: Annotated[
            str,
            MetricColumnParameterAnnotation(
                source_dataset_parameter_key="dataset",
                allowed_column_types=[
                    ScalarType(dtype=DType.TIMESTAMP),
                ],
                tag_hints=[ScopeSchemaTag.PRIMARY_TIMESTAMP],
                friendly_name="Timestamp Column",
                description="A column containing timestamp values to bucket by.",
            ),
        ],
        numeric_col: Annotated[
            str,
            MetricColumnParameterAnnotation(
                source_dataset_parameter_key="dataset",
                allowed_column_types=[
                    ScalarType(dtype=DType.INT),
                    ScalarType(dtype=DType.FLOAT),
                ],
                tag_hints=[ScopeSchemaTag.CONTINUOUS],
                friendly_name="Numeric Column",
                description="A column containing numeric values to calculate a data sketch on.",
            ),
        ],
    ) -> list[SketchMetric]:
        escaped_timestamp_col_id = escape_identifier(timestamp_col)
        escaped_numeric_col_id = escape_identifier(numeric_col)
        numeric_col_name_str = escape_str_literal(numeric_col)
        data_query = f" \
            select {escaped_timestamp_col_id} as ts, \
                   {escaped_numeric_col_id}, \
                   {numeric_col_name_str} as column_name \
            from {dataset.dataset_table_name} \
            where {escaped_numeric_col_id} is not null \
        "
        results = ddb_conn.sql(data_query).df()

        series = self.group_query_results_to_sketch_metrics(
            results,
            numeric_col,
            ["column_name"],
            "ts",
        )

        metric = self.series_to_metric(self.METRIC_NAME, series)
        return [metric]
