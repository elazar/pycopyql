from functools import reduce
from queue import Queue
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

    queue = Queue()
    for param in query_params:
        queue.put(_parse_query(param))

    data = {}
    query_history = set()
    while not queue.empty():
        _fetch(connection, meta, resolver, queue, data, query_history)

    return data

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

def _fetch(connection, meta, resolver, queue, data, query_history):
    """
    Fetches the results of a given query.

    Parameters:
        connection (sqlalchemy.engine.Connection): Connection to the database to query
        meta (sqlalchemy.schema.MetaData): Metadata for the database structure
        resolver (function): Callback for determining foreign keys corresponding to a given column
        queue (queue.Queue): Queue of queries remaining to execute
        data (dict): Data set to which the rows fetched by this function should be added
        query_history (set): Set of hashes of previously run queries, used for duplicate detection

    Returns:
        None
    """

    query = queue.get()

    query_hash = hash(frozenset(query.items()))
    if query_hash in query_history:
        return
    query_history.add(query_hash)

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
                foreign_query = { **foreign_key, 'value': value }
                queue.put(foreign_query)
