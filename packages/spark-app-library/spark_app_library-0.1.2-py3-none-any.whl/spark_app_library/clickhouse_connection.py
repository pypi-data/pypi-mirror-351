from spark_app_library.connection import Connection


class ClickhouseConnection(Connection):
    def __init__(self, host, port, database, username, password, options=None):
        driver_name = 'com.clickhouse.jdbc.ClickHouseDriver'
        source_type = 'clickhouse'
        super().__init__(host, port, database, driver_name, source_type, username, password, options)
        self.host = host
        self.port = port
        self.database = database
        self.source_type = source_type
        self.driver_name = driver_name
        self.username = username
        self.password = password
        self.options = options
        self.connection_string = f"jdbc:{self.source_type}://{self.host}:{self.port}/{self.database}"
        if self.options:
            self.connection_string = f"{self.connection_string}?{self.options}"
