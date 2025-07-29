import logging
from typing import Optional

from pyspark.sql import SparkSession, DataFrame
from spark_app_library.connection import Connection
from spark_app_library.spark_app_config import SparkAppConfig


class SparkApp:
    def __init__(self, config: SparkAppConfig):
        self.config = config
        self._setup_logger()
        self._create_spark_session()

    def _setup_logger(self, logger: Optional[logging.Logger] = None):
        """Set up the logger."""
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
            logging.basicConfig(
                level=self.config.log_level,
                format=self.config.logger_format
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
            self.spark_session = SparkSession.builder \
                .config("spark.appName", self.config.app_name) \
                .config("spark.sql.session.timeZone", self.config.time_zone) \
                .getOrCreate()
            self.spark_session.conf.set("spark.sql.adaptive.enabled", "true")
            self.spark_session.sparkContext.setLogLevel(self.config.log_level)
            return self.spark_session
        except Exception as e:
            self.logger.error(f"❌ Failed to create Spark session: {e}")
            raise

    def _log_configurations(self):
        self.logger.info(f"execution_date: {self.config.execution_date}")
        self.logger.info(f"app_name: {self.config.app_name}")
        self.logger.info(f"time_zone: {self.config.app_name}")
        self.logger.info(f"log_level: {self.config.app_name}")
        self.logger.info(f"spark_jars: {self.config.spark_jars}")
        self.logger.info(f"spark_configs: {self.config.spark_configs}")

    def get_spark_session(self):
        return self.spark_session

    def read(self,
             connection: Connection,
             dbtable: str,
             num_partition=None,
             partition_column=None,
             fetch_size=None,
             lower_bound=None,
             upper_bound=None):
        df = self.spark_session.read \
            .format("jdbc") \
            .option("url", connection.connection_string) \
            .option("user", connection.username) \
            .option("password", connection.password) \
            .option("driver", connection.driver_name) \
            .option("dbtable", dbtable) \
            .option("numPartitions", num_partition) \
            .option("partitionColumn", partition_column) \
            .option("lowerBound", lower_bound) \
            .option("upperBound", upper_bound) \
            .option("fetchsize", fetch_size) \
            .load()
        self.logger.info("Loaded.")
        return df

    def write(self,
              connection: Connection,
              df: DataFrame,
              dbtable=None,
              batch_size=None):
        df.write \
            .format("jdbc") \
            .mode("append") \
            .option("url", connection.connection_string) \
            .option("user", connection.username) \
            .option("password", connection.password) \
            .option("driver", connection.driver_name) \
            .option("dbtable", dbtable) \
            .option("batchsize", batch_size) \
            .save()
        self.logger.info(f"Successfully written results to {dbtable}")
