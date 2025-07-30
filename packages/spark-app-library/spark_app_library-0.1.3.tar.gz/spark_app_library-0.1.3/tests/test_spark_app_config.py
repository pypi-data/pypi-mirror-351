import os
import unittest
from unittest.mock import patch
from dataclasses import fields

from spark_app_library.spark_app_config import SparkAppConfig


class TestSparkAppConfig(unittest.TestCase):
    """Comprehensive test suite for SparkAppConfig class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Clear any environment variables that might interfere with tests
        env_vars_to_clear = [
            'SPARK_JARS', 'SPARK_CONFIGS', 'LOGGER_FORMAT', 'EXECUTION_DATE',
            'APP_NAME', 'TIME_ZONE', 'LOG_LEVEL', 'CUSTOM_FIELD', 'DYNAMIC_TEST'
        ]
        for var in env_vars_to_clear:
            if var in os.environ:
                del os.environ[var]

    def tearDown(self):
        """Clean up after each test method."""
        # Clear environment variables after tests
        env_vars_to_clear = [
            'SPARK_JARS', 'SPARK_CONFIGS', 'LOGGER_FORMAT', 'EXECUTION_DATE',
            'APP_NAME', 'TIME_ZONE', 'LOG_LEVEL', 'CUSTOM_FIELD', 'DYNAMIC_TEST'
        ]
        for var in env_vars_to_clear:
            if var in os.environ:
                del os.environ[var]

    def test_default_initialization(self):
        """Test that default values are properly set."""
        config = SparkAppConfig()

        # Test string defaults
        self.assertIsInstance(config.spark_jars, str)
        self.assertIn("spark-avro", config.spark_jars)
        self.assertEqual(config.logger_format,
                         "%(asctime)s | %(filename)s %(name)s - %(funcName)s - %(lineno)d | %(levelname)s - %(message)s")
        self.assertEqual(config.time_zone, "Asia/Tehran")
        self.assertEqual(config.log_level, "INFO")

        # Test None defaults
        self.assertIsNone(config.execution_date)
        self.assertIsNone(config.app_name)

        # Test dict defaults
        self.assertIsInstance(config.spark_configs, dict)
        self.assertEqual(config.spark_configs["spark.sql.session.timeZone"], "Asia/Tehran")
        self.assertEqual(config.spark_configs["spark.sql.adaptive.enabled"], "true")

        # Test internal fields
        self.assertIsInstance(config._dynamic_fields, dict)
        self.assertIsInstance(config._dynamic_defaults, dict)

    def test_initialization_with_kwargs(self):
        """Test initialization with keyword arguments."""
        config = SparkAppConfig(
            app_name="test_app",
            log_level="DEBUG",
            execution_date="2024-01-01",
            custom_field="custom_value"
        )

        # Test predefined fields
        self.assertEqual(config.app_name, "test_app")
        self.assertEqual(config.log_level, "DEBUG")
        self.assertEqual(config.execution_date, "2024-01-01")

        # Test dynamic field
        self.assertEqual(config.custom_field, "custom_value")
        self.assertIn("custom_field", config._dynamic_fields)

    @patch.dict(os.environ, {
        'APP_NAME': 'env_app',
        'LOG_LEVEL': 'ERROR',
        'TIME_ZONE': 'UTC',
        'CUSTOM_FIELD': 'env_custom'
    })
    def test_environment_variable_override(self):
        """Test that environment variables override defaults."""
        config = SparkAppConfig()

        # Test that env vars override defaults for predefined fields
        self.assertEqual(config.app_name, "env_app")
        self.assertEqual(config.log_level, "ERROR")
        self.assertEqual(config.time_zone, "UTC")

    @patch.dict(os.environ, {'APP_NAME': 'env_app'})
    def test_kwargs_override_environment(self):
        """Test that kwargs override environment variables."""
        config = SparkAppConfig(app_name="kwarg_app")

        # kwargs should take precedence over env vars
        self.assertEqual(config.app_name, "kwarg_app")

    def test_dict_field_mutability(self):
        """Test that dict fields are properly isolated between instances."""
        config1 = SparkAppConfig()
        config2 = SparkAppConfig()

        # Modify dict in first instance
        config1.spark_configs["new_key"] = "new_value"

        # Second instance should not be affected
        self.assertNotIn("new_key", config2.spark_configs)

        # Both should have original keys
        self.assertIn("spark.sql.session.timeZone", config1.spark_configs)
        self.assertIn("spark.sql.session.timeZone", config2.spark_configs)

    def test_dynamic_fields_access(self):
        """Test access to dynamic fields through __getattr__."""
        config = SparkAppConfig(
            dynamic_field1="value1",
            dynamic_field2=42,
            dynamic_field3={"nested": "dict"}
        )

        # Test different types of dynamic fields
        self.assertEqual(config.dynamic_field1, "value1")
        self.assertEqual(config.dynamic_field2, 42)
        self.assertEqual(config.dynamic_field3, {"nested": "dict"})

    def test_dynamic_fields_attribute_error(self):
        """Test that accessing non-existent attributes raises AttributeError."""
        config = SparkAppConfig()

        with self.assertRaises(AttributeError) as context:
            _ = config.non_existent_field

        self.assertIn("no attribute 'non_existent_field'", str(context.exception))

    def test_update_configs_predefined_fields(self):
        """Test updating predefined fields using update_configs."""
        config = SparkAppConfig()

        config.update_configs(
            app_name="updated_app",
            log_level="WARNING",
            spark_configs={"new": "config"}
        )

        self.assertEqual(config.app_name, "updated_app")
        self.assertEqual(config.log_level, "WARNING")
        self.assertEqual(config.spark_configs, {"new": "config"})

    def test_update_configs_dynamic_fields(self):
        """Test updating dynamic fields using update_configs."""
        config = SparkAppConfig()

        config.update_configs(
            new_dynamic_field="new_value",
            another_field=123
        )

        self.assertEqual(config.new_dynamic_field, "new_value")
        self.assertEqual(config.another_field, 123)
        self.assertIn("new_dynamic_field", config._dynamic_fields)
        self.assertIn("another_field", config._dynamic_fields)

    def test_get_config_method(self):
        """Test the _get_config helper method."""
        config = SparkAppConfig()

        # Test with arg_value (highest priority)
        result = config._get_config("test_key", "arg_value")
        self.assertEqual(result, "arg_value")

        # Test with environment variable
        with patch.dict(os.environ, {'TEST_KEY': 'env_value'}):
            result = config._get_config("test_key", None)
            self.assertEqual(result, "env_value")

        # Test with dynamic defaults
        config._dynamic_defaults["test_key"] = "default_value"
        result = config._get_config("test_key", None)
        self.assertEqual(result, "default_value")

        # Test with no value found
        result = config._get_config("unknown_key", None)
        self.assertIsNone(result)

    def test_dataclass_fields_integrity(self):
        """Test that all expected dataclass fields are present."""
        config = SparkAppConfig()
        field_names = {f.name for f in fields(config)}

        expected_fields = {
            '_dynamic_fields', '_dynamic_defaults', 'spark_jars', 'spark_configs',
            'logger_format', 'execution_date', 'app_name', 'time_zone', 'log_level'
        }

        self.assertEqual(field_names, expected_fields)

    def test_complex_data_types(self):
        """Test handling of complex data types in dynamic fields."""
        complex_data = {
            "list_field": [1, 2, 3, "four"],
            "nested_dict": {"level1": {"level2": "value"}},
            "tuple_field": (1, "two", 3.0),
            "boolean_field": True,
            "none_field": None
        }

        config = SparkAppConfig(**complex_data)

        self.assertEqual(config.list_field, [1, 2, 3, "four"])
        self.assertEqual(config.nested_dict, {"level1": {"level2": "value"}})
        self.assertEqual(config.tuple_field, (1, "two", 3.0))
        self.assertEqual(config.boolean_field, True)
        self.assertIsNone(config.none_field)

    def test_repr_and_str(self):
        """Test string representations of the config object."""
        config = SparkAppConfig(app_name="test_app")

        # Test that repr works (should not include _dynamic_fields due to repr=False)
        repr_str = repr(config)
        self.assertIn("SparkAppConfig", repr_str)
        self.assertIn("app_name='test_app'", repr_str)
        self.assertNotIn("_dynamic_fields", repr_str)

    @patch.dict(os.environ, {'DYNAMIC_TEST': 'env_dynamic_value'})
    def test_dynamic_defaults_with_environment(self):
        """Test dynamic defaults interaction with environment variables."""
        config = SparkAppConfig()
        config._dynamic_defaults["dynamic_test"] = "default_value"

        # Since the field wasn't in _dynamic_fields initially,
        # it should use the environment variable when accessed through _get_config
        result = config._get_config("dynamic_test", None)
        self.assertEqual(result, "env_dynamic_value")

    def test_field_types_validation(self):
        """Test that fields maintain their expected types."""
        config = SparkAppConfig()

        # String fields
        self.assertIsInstance(config.spark_jars, str)
        self.assertIsInstance(config.logger_format, str)
        self.assertIsInstance(config.time_zone, str)
        self.assertIsInstance(config.log_level, str)

        # Dict field
        self.assertIsInstance(config.spark_configs, dict)

        # None fields (should allow None)
        self.assertTrue(config.execution_date is None or isinstance(config.execution_date, str))
        self.assertTrue(config.app_name is None or isinstance(config.app_name, str))

    def test_dict_field_modification_and_type(self):
        """Test modification of dict fields and type verification."""
        config = SparkAppConfig()

        # Test initial state
        initial_configs = config.spark_configs.copy()
        self.assertIsInstance(config.spark_configs, dict)
        self.assertEqual(type(config.spark_configs), dict)

        # Test modification
        config.spark_configs["a"] = "b"

        # Verify modification worked
        self.assertEqual(config.spark_configs["a"], "b")
        self.assertIn("a", config.spark_configs)

        # Verify type is still dict
        self.assertIsInstance(config.spark_configs, dict)
        self.assertEqual(type(config.spark_configs), dict)

        # Verify original keys are still present
        for key, value in initial_configs.items():
            self.assertIn(key, config.spark_configs)
            self.assertEqual(config.spark_configs[key], value)

    def test_dict_field_multiple_modifications(self):
        """Test multiple modifications to dict fields."""
        config = SparkAppConfig()

        # Store original length
        original_length = len(config.spark_configs)

        # Add multiple key-value pairs
        modifications = {
            "key1": "value1",
            "key2": 42,
            "key3": {"nested": "dict"},
            "key4": [1, 2, 3],
            "key5": True
        }

        for key, value in modifications.items():
            config.spark_configs[key] = value

        # Verify all modifications
        for key, expected_value in modifications.items():
            self.assertEqual(config.spark_configs[key], expected_value)

        # Verify length increased correctly
        self.assertEqual(len(config.spark_configs), original_length + len(modifications))

        # Verify type remains dict
        self.assertEqual(type(config.spark_configs), dict)

    def test_dict_field_update_existing_keys(self):
        """Test updating existing keys in dict fields."""
        config = SparkAppConfig()

        # Get original value
        original_timezone = config.spark_configs["spark.sql.session.timeZone"]
        self.assertEqual(original_timezone, "Asia/Tehran")

        # Update existing key
        config.spark_configs["spark.sql.session.timeZone"] = "UTC"

        # Verify update
        self.assertEqual(config.spark_configs["spark.sql.session.timeZone"], "UTC")
        self.assertNotEqual(config.spark_configs["spark.sql.session.timeZone"], original_timezone)

        # Verify type is still dict
        self.assertEqual(type(config.spark_configs), dict)

    def test_dict_field_deletion(self):
        """Test deletion of keys from dict fields."""
        config = SparkAppConfig()

        # Add a key to delete
        config.spark_configs["temp_key"] = "temp_value"
        self.assertIn("temp_key", config.spark_configs)

        # Delete the key
        del config.spark_configs["temp_key"]
        self.assertNotIn("temp_key", config.spark_configs)

        # Verify type is still dict
        self.assertEqual(type(config.spark_configs), dict)

    def test_dict_field_methods_work(self):
        """Test that dict methods work properly on spark_configs."""
        config = SparkAppConfig()

        # Test keys() method
        keys = config.spark_configs.keys()
        self.assertIn("spark.sql.session.timeZone", keys)
        self.assertIn("spark.sql.adaptive.enabled", keys)

        # Test values() method
        values = config.spark_configs.values()
        self.assertIn("Asia/Tehran", values)
        self.assertIn("true", values)

        # Test items() method
        items = config.spark_configs.items()
        self.assertIn(("spark.sql.session.timeZone", "Asia/Tehran"), items)

        # Test get() method
        timezone = config.spark_configs.get("spark.sql.session.timeZone")
        self.assertEqual(timezone, "Asia/Tehran")

        default_value = config.spark_configs.get("non.existent.key", "default")
        self.assertEqual(default_value, "default")

        # Test setdefault() method
        new_value = config.spark_configs.setdefault("new.key", "new.value")
        self.assertEqual(new_value, "new.value")
        self.assertEqual(config.spark_configs["new.key"], "new.value")

        # Test pop() method
        popped_value = config.spark_configs.pop("new.key")
        self.assertEqual(popped_value, "new.value")
        self.assertNotIn("new.key", config.spark_configs)

    def test_dict_field_isolation_after_modification(self):
        """Test that dict modifications don't affect other instances."""
        config1 = SparkAppConfig()
        config2 = SparkAppConfig()

        # Modify first instance
        config1.spark_configs["instance1_key"] = "instance1_value"
        config1.spark_configs["spark.sql.session.timeZone"] = "UTC"

        # Verify second instance is unaffected
        self.assertNotIn("instance1_key", config2.spark_configs)
        self.assertEqual(config2.spark_configs["spark.sql.session.timeZone"], "Asia/Tehran")

        # Modify second instance
        config2.spark_configs["instance2_key"] = "instance2_value"

        # Verify first instance doesn't have second instance's key
        self.assertNotIn("instance2_key", config1.spark_configs)

        # Verify both maintain their own modifications
        self.assertEqual(config1.spark_configs["instance1_key"], "instance1_value")
        self.assertEqual(config2.spark_configs["instance2_key"], "instance2_value")

    def test_dict_field_reference_consistency(self):
        """Test that repeated access to dict field returns same object reference."""
        config = SparkAppConfig()

        # Get multiple references
        ref1 = config.spark_configs
        ref2 = config.spark_configs

        # They should be the same object
        self.assertIs(ref1, ref2)

        # Modification through one reference should be visible through the other
        ref1["test_key"] = "test_value"
        self.assertEqual(ref2["test_key"], "test_value")

        # Type should be consistent
        self.assertEqual(type(ref1), type(ref2))
        self.assertEqual(type(ref1), dict)

    def test_exact_scenario_from_user(self):
        """Test the exact scenario provided by the user."""
        a = SparkAppConfig()

        # Perform the exact operations
        a.spark_configs["a"] = "b"

        # Verify the results
        spark_configs_value = a.spark_configs
        spark_configs_type = type(a.spark_configs)

        # Test assertions
        self.assertIn("a", spark_configs_value)
        self.assertEqual(spark_configs_value["a"], "b")
        self.assertEqual(spark_configs_type, dict)

        # Verify original keys are still present
        self.assertIn("spark.sql.session.timeZone", spark_configs_value)
        self.assertIn("spark.sql.adaptive.enabled", spark_configs_value)

        # Verify it's a proper dict instance
        self.assertIsInstance(spark_configs_value, dict)

        # Test that we can print it (shouldn't raise any exceptions)
        str_representation = str(spark_configs_value)
        self.assertIn("'a': 'b'", str_representation)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
