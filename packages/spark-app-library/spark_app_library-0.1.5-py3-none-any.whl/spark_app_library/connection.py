class Connection:
    def __init__(self, host, port, database, driver_name, source_type, username, password, options=None):
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
