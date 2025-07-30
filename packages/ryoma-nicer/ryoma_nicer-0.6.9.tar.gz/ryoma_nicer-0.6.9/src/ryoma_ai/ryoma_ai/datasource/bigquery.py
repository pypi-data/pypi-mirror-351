import logging
from typing import Optional, Type, Any
from functools import lru_cache
import ibis
from ibis import BaseBackend
from ryoma_ai.datasource.base import SqlDataSource

# Amundsen imports for metadata pipeline
from databuilder.loader.base_loader import Loader
from databuilder.task.task import DefaultTask
from databuilder.job.job import DefaultJob
from databuilder.publisher.neo4j_csv_publisher import Neo4jCsvPublisher

# Our custom Dataplex extractor & publisher
from ryoma_ai.datasource.dataplex import DataplexMetadataExtractor, DataplexPublisher
from ryoma_ai.datasource.metadata import Catalog, Schema, Table, Column  # ensure these are correct

class BigQueryDataSource(SqlDataSource):
    def __init__(
        self,
        project_id: str,
        dataset_id: Optional[str] = None,
        credentials: Optional[Any] = None,
        metadata: Optional[Any] = None,
        *,
        metadata_extractor_cls: Type = DataplexMetadataExtractor,
        metadata_publisher_cls: Type = DataplexPublisher,
    ):
        """
        A BigQuery data source that by default crawls metadata via Google Dataplex,
        but can fall back to Amundsen BigQuery extractor + Neo4j publisher if desired.
        """
        # Tell the SqlDataSource base which 'database' (dataset) to use
        super().__init__(database=dataset_id)
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.credentials = credentials
        self.metadata = metadata
        # Pluggable extractor & publisher
        self._extractor_cls = metadata_extractor_cls
        self._publisher_cls = metadata_publisher_cls
        self.dataplex_metadata_lookup = self._build_metadata_lookup() if metadata else {}
        
    # ------------------------------------------------------------------
    # PRIVATE – single, cached BigQuery connection
    # ------------------------------------------------------------------
    def _connect(self, **kwargs) -> BaseBackend:
        """
        Build (or reuse) the Ibis BigQuery backend.

        *   Ibis ≥5.0 expects the service-account object under the keyword
            **auth_credentials** – passing “credentials” is silently ignored and
            you end up with a None backend.
        *   We cache the backend so repeated queries don’t re-authenticate.
        """
        if hasattr(self, "_backend") and self._backend is not None:
            return self._backend                                   # reuse handle

        connect_args: dict[str, Any] = {"project_id": self.project_id}
        if self.dataset_id:
            connect_args["dataset_id"] = self.dataset_id
        if self.credentials:                                        # <- renamed
            connect_args["credentials"] = self.credentials

        logging.info("Connecting to BigQuery with %r", connect_args)
        self._backend = ibis.bigquery.connect(**connect_args)
        return self._backend
        
        # ------------------------------------------------------------
    # OPTIONAL – allow callers to provide a ready-made backend
    # ------------------------------------------------------------
    def set_backend(self, backend: BaseBackend) -> "BigQueryDataSource":
        """
        Inject an already-authenticated Ibis backend (so we don’t reconnect
        over and over).  Returns *self* so you can chain calls.
        """
        self._backend = backend
        return self

    def get_catalog(self, catalog: Optional[str] = None) -> Catalog:
        return Catalog(
            catalog_name=self.dataset_id or self.project_id or "default_catalog",
            schemas=[
                Schema(
                    schema_name=table.schema if hasattr(table, "schema") else "default_schema",
                    tables=[
                        Table(
                            table_name=table.name,
                            columns=[
                                Column(
                                    name=c.name,
                                    type=getattr(c, "col_type", getattr(c, "type", "")),  # <- key line
                                    description=getattr(c, "description", ""),
                                )
                                for c in table.columns
                            ],
                        )
                    ],
                )
                for table in (self.metadata or [])
            ],
        )

    def _build_metadata_lookup(self):
        lookup = {}
        for table in self.metadata:
            fq_name = f"{self.project_id}.{table.schema}.{table.name}"
            lookup[table.name] = fq_name
        return lookup
    # ------------------------------------------------------------------
    # PUBLIC – thin helper the SqlAgent uses to run SQL
    # ------------------------------------------------------------------
    def query(self, sql: str):  # -> pandas.DataFrame
        """
        Execute *sql* immediately and return the result as a DataFrame.
        """
        return self._connect().raw_sql(sql).fetch()

# ------------------------------------------------------------
    # PRIVATE helper – make every table fully-qualified
    # ------------------------------------------------------------
    def _qualify(self, table_name):
        if table_name in self.metadata_lookup:
            return f"`{self.metadata_lookup[table_name]}`"
        elif self.dataset_id:
            return f"`{self.project_id}.{self.dataset_id}.{table_name}`"
        else:
            raise ValueError(f"Cannot qualify table '{table_name}' without dataset_id or metadata.")
    # ------------------------------------------------------------
    # PUBLIC – used by SqlQueryTool() under the hood
    # ------------------------------------------------------------
    @lru_cache(maxsize=1024)       # ask BigQuery only once per table
    def get_table_schema(self, table_name: str) -> str:
        fq_name = self._qualify(table_name)
        return (
            self._connect()
                .raw_sql(f"SELECT * FROM {fq_name} LIMIT 0")
                .schema()
                .to_string()
        )


    def crawl_catalogs(self, loader: Loader, where_clause_suffix: Optional[str] = ""):
        """
        Dynamically discover all datasets/tables/columns by:
          1) instantiating the configured metadata extractor
          2) instantiating the configured metadata publisher
          3) running the Amundsen-style DefaultJob pipeline
        """
        logging.info(
            "Crawling data catalog from BigQuery using %s",
            self._extractor_cls.__name__,
        )

        # 1) build extractor
        extractor = self._extractor_cls(
            project_id=self.project_id,
            credentials=self.credentials,
        )

        # 2) build publisher
        publisher = self._publisher_cls()

        # 3) launch the standard Amundsen load pipeline
        task = DefaultTask(extractor=extractor, loader=loader)
        job = DefaultJob(conf={}, task=task, publisher=publisher)
        job.launch()

    def get_query_plan(self, query: str):  # noqa: N802
        """
        BigQuery supports EXPLAIN; return ibis Table for profiling.
        """
        conn = self.connect()
        return conn.sql(f"EXPLAIN {query}")


class BigqueryDataSource(BigQueryDataSource):
    """
    Deprecated alias for backwards compatibility.
    """
    def __init__(self, *args, **kwargs):
        import warnings
        warnings.warn(
            "BigqueryDataSource is deprecated; please use BigQueryDataSource instead",
            DeprecationWarning,
        )
        super().__init__(*args, **kwargs)
