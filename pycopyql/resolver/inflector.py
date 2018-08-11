from inflect import engine
from re import sub

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
    foreign_column = engine().singular_noun(table) + '_id'
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

    foreign_table = engine().plural(sub('\_id$', '', column))
    if foreign_table in meta.tables:
        return [{ 'table': foreign_table, 'column': 'id' }]
    return []

def inflector(meta, table, column):
    """
    Uses inflection to return all keys related to the specified column.

    Parameters:
        meta (sqlalchemy.schema.MetaData): Metadata for the database structure
        table (string): Name of the table containing the column being examined
        column (string): Name of the column being examined

    Returns:
        list: List of dictionaries each containing the table and column of a key related to the specified column
    """

    dependencies = dependencies_inflector(meta, table, column)
    dependents = dependents_inflector(meta, table, column)
    return dependencies + dependents

