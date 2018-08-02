from sqlalchemy.sql.compiler import IdentifierPreparer
from decimal import Decimal as decimal
from datetime import date, time, datetime
import json

def get_exporter(format, exporters):
    """
    Returns an exporter based on a specified format.

    Parameters:
        format (string): 'sql' or 'json'
        exporters (dict): Dictionary of exporter names and corresponding functions that output data in correspond formats

    Returns:
        function: Exporter function for the specified format
    """

    if format in exporters:
        return exporters[format]
    if format == 'sql':
        return export_sql
    elif format == 'json':
        return export_json

    raise RuntimeError('Unsupported format: %s' % format)

def export_sql(meta, data):
    """
    Outputs data as SQL INSERT statements.

    Parameters:
        meta (sqlalchemy.schema.MetaData): Metadata for the database structure
        data: Dictionary keyed by table name of dictionaries corresponding to table rows

    Returns:
        None
    """

    tables = [table for table in meta.sorted_tables if table.name in data]
    preparer = IdentifierPreparer(meta.bind.dialect)
    prepare_column = lambda column: preparer.format_column(column, name=column.name)
    for table in tables:
        columns = ", ".join([ prepare_column(column) for column in table.columns.values() ])
        for row in data[table.name].values():
            values = list(map(_transform, list(row.values())))
            insert = "INSERT INTO %s (%s) VALUES (%s);" % (
                preparer.format_table(table, name=table.name),
                columns,
                ", ".join(values)
            )
            print(insert)

def export_json(meta, data):
    """
    Outputs data as JSON.

    Parameters:
        meta (sqlalchemy.schema.MetaData): Metadata for the database structure
        data: Dictionary keyed by table name of dictionaries corresponding to table rows

    Returns:
        None
    """

    formatted = { k: list(v.values()) for k, v in data.items() }
    print(json.dumps(formatted, cls=JSONEncoder))

def _transform(obj):
    """
    Converts values from types used by Python to types used by JSON and SQL.

    Parameters:
        obj: Python value to be converted

    Returns:
        string: String representation of the specified value
    """

    if isinstance(obj, date) or isinstance(obj, time) or isinstance(obj, datetime):
        return str(obj)
    if isinstance(obj, decimal):
        return str(float(obj))
    if obj == None: 
        return 'null'
    return str(obj)

class JSONEncoder(json.JSONEncoder):
    """
    Handles encoding data types used by SQLAlchemy that aren't handled by the
    native JSON encoder.
    """

    def default(self, obj):
        return _transform(obj)
