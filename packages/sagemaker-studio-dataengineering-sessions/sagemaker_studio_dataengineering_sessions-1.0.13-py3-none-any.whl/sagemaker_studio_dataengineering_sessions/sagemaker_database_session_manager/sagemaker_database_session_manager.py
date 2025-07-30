import json

from amazon_sagemaker_sql_execution.models.sql_execution import SQLExecutionRequest
from amazon_sagemaker_sql_execution.exceptions import CredentialsExpiredError
from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.base_session_manager import BaseSessionManager
from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.common.constants import Language, CONNECTION_TYPE_REDSHIFT
from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.common.exceptions import StartSessionException, \
     StopSessionException, SessionExpiredError, LanguageNotSupportedException
from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.common.sagemaker_connection_display import SageMakerConnectionDisplay
from .db_connection_pool import DatabaseConnectionPool
import pandas as pd
import sqlparse
from sqlparse import keywords
from sqlparse.lexer import Lexer


class SageMakerDatabaseSessionManager(BaseSessionManager):
    def __init__(self, connection_name: str):
        super().__init__()
        self.connection_name = connection_name
        self.active_connection = None
        self.connection_pool = DatabaseConnectionPool()

    def get_connection_parameter(self) -> dict:
        raise NotImplemented("get_connection_parameter has not been implemented yet")

    def create_session(self):
        # get the connection details using SageMaker CLI and translates
        # the connection details into connection props that amazon_sagemaker_sql_execution expects, calls 
        # amazon_sagemaker_sql_execution's SQL Factory to create the connection if needed.
        database_connection_properties = self.get_connection_parameter()
        try:
            self.active_connection = self.connection_pool.get_or_create_connection(
                metastore_type=None,
                metastore_id=None,
                connection_parameters=database_connection_properties,
                connection_name=self.connection_name,
            )
        except Exception as e:
            self.get_logger().error(f"Could not create session for connection {self.connection_name} because of {e.__class__.__name__}: {e}")
            raise StartSessionException(
                f"Could not create session for connection {self.connection_name} because of {e.__class__.__name__}: {e}") from e
        finally:
            del database_connection_properties

    def run_statement(self, cell="", language=Language.sql, *kwargs):
        if not language.supports_connection_type(CONNECTION_TYPE_REDSHIFT):
            raise LanguageNotSupportedException(f"Language {language.name} not supported for Redshift")

        # parse the SQL query
        # execute the SQL query using this connection
        row_limit = self.sql_result_row_limit
        sql_query = self._parse_sql_query(cell, row_limit=row_limit)
        execution_request = SQLExecutionRequest(sql_query, {})
        try:
            response = self.active_connection.execute(execution_request)
        except CredentialsExpiredError as e:
            self.get_logger().error(f"Could not run statement because of {e}")
            self.connection_pool.close_cached_connection(self.active_connection)
            self.active_connection = None
            raise SessionExpiredError(
                f"The session for SageMaker connection {self.connection_name} has expired and was closed, please rerun the query"
            )
        column_names = [
            columnMetadataEntry.name
            for columnMetadataEntry in response.column_metadata
        ]
        # We can add this as an output paramater similar to amazon_sagemaker_sql_execution
        if not response.data: # Empty Response
            return None
        if len(response.data) == 1: # Single Row (i.e., asking for count)
            return response.data[0]
        if len(response.data) == row_limit:
            SageMakerConnectionDisplay.write_msg(f"Query results have been limited to {row_limit} rows.")
        return pd.DataFrame(response.data, columns=column_names) #else return dataframe

    def _parse_sql_query(self, query, row_limit: int) -> str:
        # Strip comments from query
        # Expect a single query in statement. connection magic should already split the cell to queries.
        formatted_query = sqlparse.format(query, strip_comments=True)

        # Handle leading parenthesis during parsing as sqlparse does not do this by default
        # See https://sqlparse.readthedocs.io/en/latest/extending.html
        lex = Lexer.get_default_instance()
        leading_parenthesis_regex = ('^(\\s*\\(\\s*)+', sqlparse.tokens.Comment)
        lex.set_SQL_REGEX([leading_parenthesis_regex] + keywords.SQL_REGEX)

        # Parse SQL statements and add a LIMIT clause if the statement type is SELECT
        parsed_statement = sqlparse.parse(formatted_query)
        new_statement = parsed_statement[0].value
        if parsed_statement[0].get_type() == "SELECT":
            new_statement = f"SELECT * FROM ({parsed_statement[0].value}) as limited_subquery LIMIT {row_limit}"

        return new_statement

    def stop_session(self):
        # if active connection exists, close the active connection.
        try:
            if self.active_connection:
                self.connection_pool.close_connection(self.connection_name)
        except Exception as e:
            self.get_logger().error(f"Could not stop session for connection {self.connection_name} "
                                    f"because of {e.__class__.__name__}: {e}")
            raise StopSessionException(f"Could not stop session for connection {self.connection_name} "
                                       f"because of {e.__class__.__name__}: {e}") from e

    def is_session_connectable(self) -> bool:
        # check if active connection is not None
        if self.active_connection:
            return True
        return False

    def _configure_core(self, cell: str):
        try:
            configurations = json.loads(cell)
        except ValueError:
            SageMakerConnectionDisplay.send_error(f"Could not parse JSON object from input '{format(cell)}'")
            self.get_logger().error(f"Could not parse JSON object from input '{format(cell)}'")
            return

        if not configurations:
            SageMakerConnectionDisplay.send_error("No configuration values were provided.")
            self.get_logger().error("No configuration values were provided.")
            return

        if self.config:
            for arg, val in configurations.items():
                if hasattr(self.config, arg):
                    setattr(self.config, arg, val)

            # Filter out None value from config cache
            not_none_config = {key: value for key, value in vars(self.config).items() if value is not None}
            SageMakerConnectionDisplay.display(f"The following configurations have been updated: {not_none_config}")
