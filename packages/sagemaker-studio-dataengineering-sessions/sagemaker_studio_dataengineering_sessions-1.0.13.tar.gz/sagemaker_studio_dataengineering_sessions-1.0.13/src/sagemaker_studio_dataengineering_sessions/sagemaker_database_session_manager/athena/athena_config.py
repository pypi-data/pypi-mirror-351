class Config:
    def __init__(self):
        # PyAthena connection
        # https://github.com/laughingman7743/PyAthena/blob/master/pyathena/connection.py#L49
        self.catalog_name = None
        self.schema_name = None