from functools import reduce
from inflect import engine as inflector
from re import sub, split
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

def dependents_inflector(meta, table, column):
    """
    Uses inflection of column names to return foreign keys from tables that reference the specified column if it is a primary key.

    Parameters:
        meta (sqlalchemy.schema.MetaData): Metadata for the database structure
        table (string): Name of the table containing the column being examined
        column (string): Name of the column being examined

    Returns:
        list: List of dictionaries each containing the table and column of foreign key columns that reference the specified column
    """

    if column != 'id':
        return []
    foreign_column = inflector().singular_noun(table) + '_id'
    foreign_tables = [table for table in meta.tables if foreign_column in meta.tables[table].columns]
    make_key = lambda table: { 'table': table, 'column': foreign_column }
    return list(map(make_key, foreign_tables))

def dependencies_inflector(meta, table, column):
    """
    Uses inflection of column names to return the corresponding primary key column for a specified column if it is a foreign key.

    Parameters:
        meta (sqlalchemy.schema.MetaData): Metadata for the database structure
        table (string): Name of the table containing the column being examined
        column (string): Name of the column being examined
        
    Returns:
        list: List with a single dictionary containing the table and column of the primary key column, or an empty list
    """

    foreign_table = inflector().plural(sub('\_id$', '', column))
    if foreign_table in meta.tables:
        return [{ 'table': foreign_table, 'column': 'id' }]
    return []

def dependents_foreign_key(meta, table, column):
    """
    Uses foreign key constraints to return foreign keys from tables that reference the specified column if it is a primary key.

    Parameters:
        meta (sqlalchemy.schema.MetaData): Metadata for the database structure
        table (string): Name of the table containing the column being examined
        column (string): Name of the column being examined

    Returns:
        list: List of dictionaries each containing the table and column of foreign key columns that reference the specified column
    """

    primary_table = meta.tables[table]
    primary_key = primary_table.primary_key
    if len(primary_key.columns) != 1:
        return []

    primary_column = list(primary_key.columns)[0]
    if primary_column.name != column:
        return []

    filter_column = lambda key: len(key.elements) == 1 and key.elements[0].column == primary_column
    foreign_keys = list(filter(filter_column, _get_all_keys(meta)))

    get_column = lambda key: list(key.columns)[0]
    columns = list(map(get_column, foreign_keys))
    return _keys_from_columns(columns)

def dependencies_foreign_key(meta, table, column):
    """
    Uses foreign key constraints to return the corresponding primary key column for a specified column if it is a foreign key.

    Parameters:
        meta (sqlalchemy.schema.MetaData): Metadata for the database structure
        table (string): Name of the table containing the column being examined
        column (string): Name of the column being examined
        
    Returns:
        list: List with a single dictionary containing the table and column of the primary key column, or an empty list
    """

    foreign_column = meta.tables[table].columns[column]
    filter_column = lambda key: len(key.columns) == 1 and list(key.columns)[0] == foreign_column
    foreign_keys = list(filter(filter_column, _get_all_keys(meta)))

    get_primary_column = lambda key: key.elements[0].column
    columns = list(map(get_primary_column, foreign_keys))
    return _keys_from_columns(columns)

def _get_all_keys(meta):
    get_all_keys = lambda keys, table: keys + list(table.foreign_key_constraints)
    return reduce(get_all_keys, meta.tables.values(), [])

def _keys_from_columns(columns):
    make_key = lambda column: { 'table': column.table.name, 'column': column.name }
    return list(map(make_key, columns))
