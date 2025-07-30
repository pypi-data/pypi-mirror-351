# Spark App Library: Usage Guide

This guide demonstrates how to use the Spark App Library to build and run Spark applications.

## Installation

To install from pypi:

    pip install spark-app-library

Released versions on package registry:

    https://gitlab.snapp.ir/data-team/data-engineering/apache-spark/spark-app-library/-/packages

This package has been already installed on `de-spark-image`.

## Prerequisites

Ensure you have the necessary classes imported:

```python
from spark_app_library.clickhouse_connection import ClickhouseConnection
from spark_app_library.spark_app import SparkApp
from spark_app_library.spark_app_config import SparkAppConfig
```

## Core Workflow

A typical application using this library follows these steps:

1.  **Initialization**: Set up configurations and create the main Spark application object.
2.  **Read Input Data**: Load data from your source database.
3.  **Transformations**: Apply your business logic using PySpark DataFrame operations.
4.  **Write Output Data**: Save the processed data to your target database.

Let's break down each step.

---

### Step 1: Initialization

First, you need to configure your application and set up connections.

#### a. Configure the Spark Application (`SparkAppConfig`)

The `SparkAppConfig` class holds all your application settings. You can set a name for your Spark application and provide other configurations. Many settings have defaults, but you can override them.

```python
# Minimal configuration: just an app name
config = SparkAppConfig(app_name="funnel-cab-app-open")

# You can also pass other predefined configs or even dynamic ones:
# config = SparkAppConfig(
#     app_name="my-complex-app",#     log_level="DEBUG",
#     execution_date="2025-05-31", # Example: often passed dynamically
#     my_custom_param="custom_value" # Dynamic config
# )
```

*   The `SparkAppConfig` can automatically pick up configurations from environment variables (e.g., `EXECUTION_DATE` for `execution_date`).
*   You can access these configurations later using `config.app_name`, `config.execution_date`, etc.

#### b. Define Database Connections (`ClickhouseConnection` / `PostgreSQLConnection`)

Use the `Connection` class or its specific variants like `ClickhouseConnection` and `PostgreSQLConnection` to define how to connect to your databases.

```python
# Connection for reading/writing data
clickhouse_connection = ClickhouseConnection(
    host="172.21.16.1",
    port="8123",
    database="default",
    username=os.getenv("CH_USER"),
    password=os.getenv("CH_PASSWORD"),
    options="socket_timeout=999999999&connect_timeout=999999999" # Optional JDBC parameters
)
```
*   The `ClickhouseConnection` automatically sets the correct JDBC driver and source type for ClickHouse.
*   Store sensitive information like usernames and passwords in environment variables.

#### c. Create the Spark Application Instance (`SparkApp`)

Instantiate `SparkApp` with your configuration. This will set up the Spark session and logging.

```python
spark_app = SparkApp(config)
```
*   This step creates a `SparkSession` based on the settings in your `config` object (e.g., `spark_jars`, `spark_configs`).

---

### Step 2: Read Input DataFrames

Use the `spark_app.read()` method to load data from your source database into a Spark DataFrame.

```python
# Define your SQL query or table name
# Using f-string to inject execution_date from config
funnel_cab_app_open_query = f"""(
  SELECT
        user_id,
        device_type,
        os_version,
        timestamp_time
    FROM 
        snapp_raw_log.config_request
    WHERE 
        user_type = 'passenger' AND
        user_id is not NULL
        AND created_date = '{config.execution_date}' 
) as funnel_cab_app_open_raw
"""

# Read data using the defined connection and query
df_cab_funnel_app_open = spark_app.read(
    connection=clickhouse_connection,      # The connection object defined earlier
    dbtable=funnel_cab_app_open_query,     # Table name or a subquery string (as shown)
    num_partition=6,                       # Optional: Number of Spark partitions for parallelism
    partition_column="timestamp_time",     # Optional: Column to use for partitioning reads
    fetch_size=100000,                     # Optional: JDBC fetch size
    # Optional: Explicitly define bounds for partitioned reads
    lower_bound=f"{config.execution_date} 00:00:00", 
    upper_bound=f"{(datetime.strptime(config.execution_date,'%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')} 00:00:00",
)
```
*   **`connection`**: Pass the `Connection` object you created.
*   **`dbtable`**: This can be a simple table name (e.g., `"my_schema.my_table"`) or a full SQL subquery enclosed in parentheses and aliased (e.g., `(SELECT * FROM ...) as my_alias`).
*   **Partitioning (`num_partition`, `partition_column`, `lower_bound`, `upper_bound`)**: These options are crucial for reading large tables efficiently by distributing the read load across Spark executors.
    *   If `partition_column` is provided but `lower_bound` and `upper_bound` are not, the library will attempt to query the min/max values of `partition_column` from the table to set them automatically.
*   **`fetch_size`**: Controls how many rows are fetched from the database per round trip.

---

### Step 3: Transformations

Once you have your DataFrame (`df_cab_funnel_app_open` in the example), you apply your business logic using standard PySpark DataFrame transformations. This library focuses on the I/O and setup, not the transformations themselves.

```python
# Example PySpark transformations (your logic goes here)
result_df = (
    df_cab_funnel_app_open
    .withColumn(
        "created_at", to_utc_timestamp(col("timestamp_time"), "Asia/Tehran")
    )
    .select(
        col("user_id").alias("snapp_id"),
        col("created_at"),
        lit("app_open").alias("stage_type"),
        col("details")
    )
)
```

---

### Step 4: Write the Result

After transforming your data, use the `spark_app.write()` method to save the resulting DataFrame to your target database.

```python
spark_app.write(
    connection=clickhouse_output_connection, # The connection object for your target database
    df=result_df,                            # The DataFrame to write
    dbtable="database.target_table",         # The target table name (e.g., "schema.table_name")
    output_mode="append",                    # Optional: Spark save mode (default is "append")
                                             # Other modes: "overwrite", "error", "ignore"
    batch_size=100000                        # Optional: JDBC batch size for writing
)
```
*   **`connection`**: Pass the `Connection` object for the destination.
*   **`df`**: The final DataFrame you want to save.
*   **`dbtable`**: The name of the table where data will be written.
*   **`output_mode`**: Specifies how to handle existing data in the table.
*   **`batch_size`**: Controls how many rows are sent to the database in each batch during the write operation.

---
