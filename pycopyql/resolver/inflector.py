from inflect import engine
from re import sub

def singular(table):
    inflected = engine().singular_noun(table)
    return inflected and (inflected + '_id') or table

def plural(column):
    return engine().plural(sub('\_id$', '', column)) or column

def dependents_inflector(meta, table, column, inflector=singular):
    """
    Uses inflection of column names to return foreign keys from tables that reference the specified column if it is a primary key.

    Parameters:
        meta (sqlalchemy.schema.MetaData): Metadata for the database structure
        table (string): Name of the table containing the column being examined
        column (string): Name of the column being examined
        inflector (function): Inflects a given table name, using its singular or original form by default

    Returns:
        list: List of dictionaries each containing the table and column of foreign key columns that reference the specified column
    """

    primary = list(meta.tables[table].primary_key.columns)[0].name
    if column != primary:
        return []
    foreign_column = inflector(table)
    foreign_tables = [table for table in meta.tables if foreign_column in meta.tables[table].columns]
    make_key = lambda table: { 'table': table, 'column': foreign_column }
    return list(map(make_key, foreign_tables))

def dependencies_inflector(meta, table, column, inflector=plural):
    """
    Uses inflection of column names to return the corresponding primary key column for a specified column if it is a foreign key.

    Parameters:
        meta (sqlalchemy.schema.MetaData): Metadata for the database structure
        table (string): Name of the table containing the column being examined
        column (string): Name of the column being examined
        inflector (function): Inflects a given column name, using its plural or original form by default

    Returns:
        list: List with a single dictionary containing the table and column of the primary key column, or an empty list
    """

    foreign_table = inflector(column)
    if foreign_table in meta.tables:
        foreign_column = list(meta.tables[foreign_table].primary_key.columns)[0].name
        return [{ 'table': foreign_table, 'column': foreign_column }]
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

