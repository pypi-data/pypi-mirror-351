from typing import TYPE_CHECKING, Optional, Union

import mlflow
from mlflow.tracking import fluent

from databricks.rag_eval import context
from databricks.sdk import WorkspaceClient

from .entities import Dataset

if TYPE_CHECKING:
    from databricks.rag_eval.clients.managedevals.managed_evals_client import (
        ManagedEvalsClient,
    )


def _get_client() -> "ManagedEvalsClient":
    from databricks.rag_eval.clients.managedevals.managed_evals_client import (
        ManagedEvalsClient,  # noqa: F401
    )

    @context.eval_context
    def getter():
        return context.get_context().build_managed_evals_client()

    return getter()


def create_dataset(
    uc_table_name: str, experiment_id: Optional[Union[str, list[str]]] = None
) -> Dataset:
    """Create a dataset with the given name and associate it with the given experiment.

    Args:
        uc_table_name: The UC table location of the dataset.
        experiment_id: The ID of the experiment to associate the dataset with. If not provided,
            the current experiment is inferred from the environment.
    """
    if not experiment_id:
        # Infer the experiment ID from the current environment.
        experiment_id = fluent._get_experiment_id()
        if experiment_id == mlflow.tracking.default_experiment.DEFAULT_EXPERIMENT_ID:
            raise ValueError(
                "Please provide an experiment_id or run this code within an active experiment."
            )

    if isinstance(experiment_id, str):
        experiment_id = [experiment_id]

    dataset = _get_client().create_dataset(
        uc_table_name=uc_table_name, experiment_ids=experiment_id
    )
    # Insert 0 rows to set the table schema so that spark.table(uc_table_name) works.
    dataset.insert([])
    return dataset


def get_dataset(uc_table_name: str) -> Dataset:
    """Get the dataset with the given name."""
    w = WorkspaceClient()
    dataset_id = w.tables.get(uc_table_name).table_id
    return _get_client().get_dataset(dataset_id=dataset_id)


def delete_dataset(uc_table_name: str) -> None:
    """Delete the dataset with the given name."""
    w = WorkspaceClient()
    dataset_id = w.tables.get(uc_table_name).table_id
    _get_client().delete_dataset(dataset_id=dataset_id)
