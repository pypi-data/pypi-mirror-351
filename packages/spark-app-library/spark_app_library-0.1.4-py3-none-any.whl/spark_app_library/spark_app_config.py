import json
import os
from dataclasses import dataclass, field, fields as dataclass_fields, MISSING
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
        "spark.sql.adaptive.enabled": "true"
    }, init=True)

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
        # Get all Field objects for this dataclass
        class_field_definitions = {f.name: f for f in dataclass_fields(self)}

        # Initialize init=False fields (_dynamic_fields, _dynamic_defaults)
        #   from their factories, unless they are provided in kwargs.
        if '_dynamic_fields' in kwargs:
            self._dynamic_fields = kwargs['_dynamic_fields']
        else:
            self._dynamic_fields = class_field_definitions['_dynamic_fields'].default_factory()

        if '_dynamic_defaults' in kwargs:
            self._dynamic_defaults = kwargs['_dynamic_defaults']
        else:
            self._dynamic_defaults = class_field_definitions['_dynamic_defaults'].default_factory()

        # Setting initial values for all predefined (init=True) fields using dataclass defaults/factories.
        for field_name, f_obj in class_field_definitions.items():
            if f_obj.init:  # Process only init=True fields here for defaults
                if field_name not in kwargs:
                    if f_obj.default is not MISSING:
                        setattr(self, field_name, f_obj.default)
                    elif f_obj.default_factory is not MISSING:
                        setattr(self, field_name, f_obj.default_factory())

        # Override with environment variables for predefined fields.
        for field_name, f_obj in class_field_definitions.items():
            if f_obj.init:  # Only init=True fields
                env_value_str = os.getenv(field_name.upper())
                if env_value_str is not None:
                    current_value = getattr(self, field_name, None)
                    if isinstance(current_value, dict):
                        try:
                            # Attempt to parse as JSON if it's a dict field.
                            parsed_env_value = json.loads(env_value_str)
                            if isinstance(parsed_env_value, dict):
                                setattr(self, field_name, parsed_env_value)
                            else:
                                setattr(self, field_name, env_value_str)
                        except json.JSONDecodeError:
                            setattr(self, field_name, env_value_str)
                    else:
                        setattr(self, field_name, env_value_str)

        # Process all kwargs:
        #   - If key is a defined field (init=True or init=False), update it (overrides defaults/env).
        #   - If key is not a defined field, add to _dynamic_fields.
        for key, value in kwargs.items():
            if key in class_field_definitions:
                setattr(self, key, value)
            else:
                self._dynamic_fields[key] = value

        # Apply defaults for dynamic fields (from _dynamic_defaults specification).
        #   This uses the self._dynamic_defaults dictionary that was initialized.
        if isinstance(self._dynamic_defaults, dict):
            for key_in_default_spec, default_val_for_dynamic in self._dynamic_defaults.items():
                if key_in_default_spec not in self._dynamic_fields:
                    env_val_for_dynamic = os.getenv(key_in_default_spec.upper())
                    if env_val_for_dynamic is not None:
                        self._dynamic_fields[key_in_default_spec] = env_val_for_dynamic
                    else:
                        self._dynamic_fields[key_in_default_spec] = default_val_for_dynamic

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
