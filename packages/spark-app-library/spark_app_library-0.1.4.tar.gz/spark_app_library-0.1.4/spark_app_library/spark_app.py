import logging
from typing import Optional
from pyspark.sql import SparkSession, DataFrame
from spark_app_library.connection import Connection
from spark_app_library.spark_app_config import SparkAppConfig


class SparkApp:
    def __init__(self, config: SparkAppConfig):
        self._config = config
        self._setup_logger()
        self._create_spark_session()
        self._log_configurations()

    def _setup_logger(self, logger: Optional[logging.Logger] = None):
        """Set up the logger."""
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
            logging.basicConfig(
                level=self._config.log_level,
                format=self._config.logger_format
            )

    def _create_spark_session(self):
        """
        Create and configure a Spark session.

        Returns:
            SparkSession: Configured Spark session

        Raises:
            Exception: If Spark session creation fails
        """
        try:
            self._spark_session = SparkSession.builder \
                .config("spark.appName", self._config.app_name) \
                .config("spark.sql.session.timeZone", self._config.time_zone) \
                .getOrCreate()
            for key, value in self._config.spark_configs.items():
                self._spark_session.conf.set(key, value)
            self._spark_session.sparkContext.setLogLevel(self._config.log_level)
            self.logger.info(f"✅ Spark session has been created successfully.")
            return self._spark_session
        except Exception as e:
            self.logger.error(f"❌ Failed to create spark session: {e}")
            raise

    def _log_configurations(self):
        """Logs the non-secure configurations."""
        self.logger.info(f"execution_date: {self._config.execution_date}")
        self.logger.info(f"app_name: {self._config.app_name}")
        self.logger.info(f"time_zone: {self._config.app_name}")
        self.logger.info(f"log_level: {self._config.app_name}")
        self.logger.info(f"spark_jars: {self._config.spark_jars}")
        self.logger.info(f"spark_configs: {self._config.spark_configs}")

    def get_spark_session(self):
        """Returns the internal spark session."""
        return self._spark_session

    def get_config(self):
        """Returns the internal spark app configuration."""
        return self._config

    def _get_bounds(self, connection: Connection, partition_column: str, dbtable: str):
        self.logger.info(f"Getting partition bounds for {dbtable}...")
        query = f"SELECT min({partition_column}) as lower_bound, max({partition_column}) as upper_bound FROM {dbtable}"
        self.logger.info(f"Getting partition bounds query is: {query}")
        data_info = (
            self._spark_session.read.format("jdbc")
            .option("url", connection.connection_string)
            .option("driver", connection.driver_name)
            .option("query", query)
            .option("user", connection.username)
            .option("password", connection.password)
            .load()
        )
        row = data_info.first()
        if row is None:
            raise ValueError("❌ No data found in the table to get partition bounds.")
        else:
            self.logger.info(f"Lower and upper bounds are: {row['lower_bound']}, {row['upper_bound']}")
            return row['lower_bound'], row['upper_bound']

    def read(self,
             connection: Connection,
             dbtable: str,
             num_partition=None,
             partition_column=None,
             fetch_size=100000,
             lower_bound=None,
             upper_bound=None):
        self.logger.info(f"Loading from {connection.source_type}...")
        self.logger.info(f"Database table to load is {dbtable}")
        df = self._spark_session.read \
            .format("jdbc") \
            .option("url", connection.connection_string) \
            .option("user", connection.username) \
            .option("password", connection.password) \
            .option("driver", connection.driver_name) \
            .option("dbtable", dbtable)
        self.logger.info(f"Spark reader driver: {connection.driver_name}")
        if num_partition:
            df = df.option("numPartitions", num_partition)
            self.logger.info(f"Spark reader numPartitions: {num_partition}")
        if partition_column:
            df = df.option("partitionColumn", partition_column)
            self.logger.info(f"Spark reader partitionColumn: {partition_column}")
        if not lower_bound and not upper_bound:
            lower_bound, upper_bound = self._get_bounds(connection, partition_column, dbtable)
            self.logger.info(f"Spark reader lower_bound: {lower_bound}")
            self.logger.info(f"Spark reader upper_bound: {upper_bound}")
        if lower_bound:
            df = df.option("lowerBound", lower_bound)
            self.logger.info(f"Spark reader lower_bound: {lower_bound}")
        if upper_bound:
            df = df.option("upperBound", upper_bound)
            self.logger.info(f"Spark reader upper_bound: {upper_bound}")
        if fetch_size:
            df = df.option("fetchsize", fetch_size)
            self.logger.info(f"Spark reader fetchsize: {fetch_size}")
        df = df.load()
        self.logger.info(f"✅ Successfully loaded data from {connection.source_type}.")
        return df

    def write(self,
              connection: Connection,
              df: DataFrame,
              dbtable: str,
              output_mode: str = "append",
              batch_size=100000):
        df = df.write \
            .format("jdbc") \
            .mode(output_mode) \
            .option("url", connection.connection_string) \
            .option("user", connection.username) \
            .option("password", connection.password) \
            .option("driver", connection.driver_name) \
            .option("dbtable", dbtable)
        self.logger.info(f"Spark writer driver: {connection.driver_name}")
        self.logger.info(f"Spark writer dbtable: {dbtable}")
        if batch_size:
            df = df.option("batchsize", batch_size)
            self.logger.info(f"Spark writer batchsize: {batch_size}")
        df.save()
        self.logger.info(f"✅ Successfully written results to {dbtable}")
