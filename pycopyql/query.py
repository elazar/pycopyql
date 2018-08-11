from functools import reduce
from re import split
from sqlalchemy.sql import select

def query(connection, meta, resolver, query_params):
    """
    Executes one or more queries against a database and returns the results.

    Parameters:
        connection (sqlalchemy.engine.Connection): Connection to the database to query
        meta (sqlalchemy.schema.MetaData): Metadata for the database structure
        resolver (function): Callback for determining foreign keys corresponding to a given column
        query_params (list): One or more query strings of the format TABLE.COLUMN:VALUE

    Returns:
        dict: Dictionary keyed by table name of dictionaries corresponding to table rows
    """

    queries = [_parse_query(param) for param in query_params]
    execute_query = lambda data, query: _fetch(connection, meta, resolver, query, data)
    return reduce(execute_query, queries, {})

def _parse_query(query):
    """
    Parses a query string into its components.

    Parameters:
        query (string): String of the format TABLE.COLUMN:VALUE

    Returns:
        dict: Dictionary containing the table, column, and value from the query string
    """

    table, column, value = split('\.|:', query)
    return { 'table': table, 'column': column, 'value': value }

def _fetch(connection, meta, resolver, query, data):
    """
    Fetches the results of a given query.

    Parameters:
        connection (sqlalchemy.engine.Connection): Connection to the database to query
        meta (sqlalchemy.schema.MetaData): Metadata for the database structure
        resolver (function): Callback for determining foreign keys corresponding to a given column
        query (dict): Query parameters as returned by _parse_query()
        data (dict): Data set to which the rows fetched by this function should be added

    Returns:
        dict: Copy of the data parameter with any fetched rows added to it
    """

    # If this query has already been executed, return data unmodified
    if query['table'] in data:
        find_row = lambda row: row[query['column']] == query['value']
        if len(list(filter(find_row, data[query['table']].values()))) > 0:
            return data

    table = meta.tables[query['table']]
    s = select([table]).where(table.c[query['column']] == query['value'])
    for row in connection.execute(s):
        row_hash = hash(frozenset(row.items()))
        row = dict(row.items())
        if not table.name in data:
            data[table.name] = {}
        elif row_hash in data[table.name]:
            continue
        data[table.name][row_hash] = row
        for column, value in row.items():
            foreign_keys = resolver(meta, table.name, column)
            for foreign_key in foreign_keys:
                foreign_query = { **foreign_key, 'value': str(value) }
                data = _fetch(connection, meta, resolver, foreign_query, data)

    return data
