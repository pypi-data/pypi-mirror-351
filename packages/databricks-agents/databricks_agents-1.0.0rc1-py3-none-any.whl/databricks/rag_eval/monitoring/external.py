import pyspark

from databricks.agents.utils.uc import _sanitize_model_name
from databricks.rag_eval.utils import uc_utils


def build_endpoint_name(monitoring_table_name: str) -> str:
    """Builds the name of the serving endpoint associated with a given monitoring table.

    Args:
        monitoring_table_name (str): The name of the monitoring table.

    Returns:
        str: The name of the serving endpoint.
    """
    prefix = "monitor_"
    truncated_monitoring_table_name = monitoring_table_name[
        : uc_utils.MAX_UC_ENTITY_NAME_LEN - len(prefix)
    ]
    sanitized_truncated_model_name = _sanitize_model_name(
        truncated_monitoring_table_name
    )
    return f"{prefix}{sanitized_truncated_model_name}"


def create_monitoring_table(
    monitoring_table: uc_utils.UnityCatalogEntity,
):
    spark = pyspark.sql.SparkSession.builder.getOrCreate()
    # This will create the table without the schema. The schema will be inferred from the
    # first batch of data when data is streamed in from the monitoring job.
    query = f"""CREATE TABLE IF NOT EXISTS {monitoring_table.fullname_with_backticks} (
        databricks_request_id STRING,
        trace STRING,
        status STRING,
        request STRING, 
        request_raw STRING,
        timestamp TIMESTAMP,
        evaluation_status STRING,
        execution_time_ms LONG
    )"""
    spark.sql(query)
