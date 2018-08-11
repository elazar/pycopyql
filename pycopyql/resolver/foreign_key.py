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

def foreign_key(meta, table, column):
    """
    Uses foreign key constraints to return all keys related to the specified column.

    Parameters:
        meta (sqlalchemy.schema.MetaData): Metadata for the database structure
        table (string): Name of the table containing the column being examined
        column (string): Name of the column being examined

    Returns:
        list: List of dictionaries each containing the table and column of a key related to the specified column
    """

    dependencies = dependencies_foreign_key(meta, table, column)
    dependents = dependents_foreign_key(meta, table, column)
    return dependencies + dependents

