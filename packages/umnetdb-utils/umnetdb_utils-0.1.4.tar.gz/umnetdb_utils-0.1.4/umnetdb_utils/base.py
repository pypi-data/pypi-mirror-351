
from typing import Union
from os import getenv
import re
import logging
from decouple import Config, RepositoryEnv

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class UMnetdbBase:
    """
    Base helper class
    """
    # set in child classes - you can use environment variables within curly braces here
    URL = None

    def __init__(self, env_file:str=".env"):
        """
        Initiate a umnetdb object. Optionally provide a path to a file with environment variables
        containing the credentials for the database. If no file is provided and there's no ".env",
        the code will look in the user's environment (os.getenv) for these values.
        """

        try:
            self._env = Config(RepositoryEnv(env_file))
        except FileNotFoundError:
            self._env = {}

        self.url = self._resolve_url()

        self.engine = create_engine(self.url)
        self.session = None

    def _resolve_url(self) -> str:
        """
        Resolves any reference to environment variables in the url attribute
        and returns the string. The string should use curly braces to indicate an environment
        variable
        """
        url = self.URL
        for m in re.finditer(r"{(\w+)}", url):
            var = m.group(1)
            val = self._env.get(var, getenv(var))

            if not val:
                raise ValueError(f"Undefined environment variable {var} in {url}")
            url = re.sub(r"{" + var + "}", val, url)

        return url

    def open(self):
        """
        Create a new session to the database if there isn't one already
        """
        if not self.session:
            self.session = Session(self.engine)

    def close(self):
        """
        Closes db session if there is one
        """
        if self.session:
            self.session.close()
            self.session = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, fexc_type, exc_val, exc_tb):
        self.close()

    def __getattr__(self, val:str):
        if self.session:
            return getattr(self.session, val)

        raise AttributeError(self)

    def _build_select(self, select, table, joins=None, where=None, order_by=None, limit=None, group_by=None, distinct=False) -> str:
        '''
        Generic 'select' query string builder built from standard query components as input.
        The user is required to generate substrings for the more complex inputs
        (eg joins, where statements), this function just puts all the components
        together in the right order with appropriately-added newlines (for debugging purposes)
        and returns the result.

        :select: a list of columns to select
          ex: ["nip.mac", "nip.ip", "n.switch", "n.port"]
        :table: a string representing a table (or comma-separated tables, with our without aliases)
          ex: "node_ip nip"
        :joins: a list of strings representing join statements. Include the actual 'join' part!
          ex: ["join node n on nip.mac = n.mac", "join device d on d.ip = n.switch"]
        :where: For a single where statement, provide a string. For multiple provide a list. 
           The list of statements are "anded". If you need "or", embed it in one of your list items
           DO NOT provide the keyword 'where' - it is auto-added.
          ex: ["node_ip.ip = '1.2.3.4'", "node.switch = '10.233.0.5'"]
        :order_by: A string representing a column name (or names) to order by
        :group_by: A string representing a column name (or names) to group by
        :limit: An integer

        '''

        # First part of the sql statement is the 'select'
        distinct = 'distinct ' if distinct else ''
        sql = f"select {distinct}" + ", ".join(select) + "\n"

        # Next is the table
        sql += f"from {table}\n"

        # Now are the joins. The 'join' keyword(s) need to be provided
        # as part of the input, allowing for different join types
        if joins:
            for j in joins:
                sql += f"{j}\n"

        # Next are the filters. They are 'anded'
        if where and isinstance(where, list):
            
            sql += "where\n"
            sql += " and\n".join(where) + "\n"
        elif where:
            sql += f"where {where}\n"

        # Finally the other options
        if order_by:
            sql += f"order by {order_by}\n"

        if group_by:
            sql += f"group by {group_by}\n"

        if limit:
            sql += f"limit {limit}\n"
        
        logger.debug(f"Generated SQL command:\n****\n{sql}\n****\n")

        return sql

    def _execute(self, sql:str, rows_as_dict:bool=True, fetch_one:bool=False):
        '''
        Generic sqlalchemy "open a session, execute this sql command and give me all the results"

        NB This function is defined for legacy database classes that came from umnet-scripts.
        It's encouraged to use "self.session.execute" in other child methods, allowing
        scripts that import the child class to use the context manager and execute multiple
        mehtods within the same session.
        '''
        with self.engine.begin() as c:
            r = c.execute(text(sql))

        rows = r.fetchall()
        if rows and rows_as_dict:
            return [r._mapping for r in rows]
        elif rows:
            return rows
        else:
            return []

        
    def execute(self, sql:str, rows_as_dict:bool=True, fetch_one:bool=False) -> Union[list[dict],dict]:
        """
        Executes a sqlalchemy command and gives all the results as a list of dicts, or as a dict
        if 'fetch_one' is set to true.
        Does not open a session - you must open one yourself.
        """
        result = self.session.execute(text(sql))

        if rows_as_dict:
            result = result.mappings()

        if fetch_one:
            return dict(result.fetchone())
        
        return [dict(r) for r in result.fetchall()]