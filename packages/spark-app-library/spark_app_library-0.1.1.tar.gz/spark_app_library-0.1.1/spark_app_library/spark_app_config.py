import os
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class SparkAppConfig:
    """Configuration container for SparkSinkConnector with dynamic fields and default values support."""
    _dynamic_fields: Dict[str, Any] = field(default_factory=dict, init=False, repr=False)
    _dynamic_defaults: Dict[str, Any] = field(default_factory=lambda: {}, init=False, repr=False)

    # spark session default configs
    spark_jars: str = ("org.apache.spark:spark-avro_2.12:3.5.1,"
                       "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,"
                       "org.apache.kafka:kafka-clients:3.9.0,"
                       "org.apache.spark:spark-protobuf_2.12:3.5.1")

    spark_configs: dict = field(default_factory=lambda: {
        "spark.sql.session.timeZone": "Asia/Tehran",
        "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
        "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
        "spark.sql.legacy.timeParserPolicy": "LEGACY",
        "spark.databricks.delta.retentionDurationCheck.enabled": "false",
        "spark.sql.catalogImplementation": "hive"
    })

    # logger default configs
    logger_format: str = "%(asctime)s | %(filename)s %(name)s - %(funcName)s - %(lineno)d | %(levelname)s - %(message)s"
    execution_date: str = None
    app_name: str = None
    time_zone: str = "Asia/Tehran"
    log_level: str = "INFO"

    def __init__(self, **kwargs):
        """
        Custom __init__ method to allow dynamic fields to be passed as keyword arguments.
        """
        # Explicitly initialize _dynamic_fields
        self._dynamic_fields = {}
        predefined_fields = {f.name for f in self.__dataclass_fields__.values()}

        for field_name in predefined_fields:
            if field_name not in ('_dynamic_defaults', '_dynamic_fields'):
                if os.getenv(field_name.upper()) is not None:
                    setattr(self, field_name, os.getenv(field_name.upper()))

        for key, value in kwargs.items():
            if key in predefined_fields:
                setattr(self, key, value)
            else:
                self._dynamic_fields[key] = value

        # Initialize defaults for predefined fields
        field_name = '_dynamic_defaults'
        default_value = self.__dataclass_fields__[field_name].default_factory()
        setattr(self, field_name, default_value)

        # Apply defaults for dynamic fields
        for key, default_value in self._dynamic_defaults.items():
            if key not in self._dynamic_fields:
                self._dynamic_fields[key] = os.getenv(key.upper(), default_value)

    def _get_config(self, key, arg_value):
        """
        Retrieves configuration, prioritizing existing attribute value (from constructor),
        then environment variables, then defaults.
        """
        if arg_value is not None:
            return arg_value

        env_key = key.upper()
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value

        # Default values for dynamic fields
        if key in self._dynamic_defaults:
            return self._dynamic_defaults[key]

        return None

    def update_configs(self, **kwargs):
        """
        updates the configurations
        """
        predefined_fields = {f.name for f in self.__dataclass_fields__.values()}
        for key, value in kwargs.items():
            if key in predefined_fields:
                setattr(self, key, value)
            else:
                self._dynamic_fields[key] = value

    def __getattr__(self, key):
        """
        Override __getattr__ to retrieve dynamic fields from _dynamic_fields.
        """
        if key in self._dynamic_fields:
            return self._dynamic_fields[key]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")
