# pycopyql

Exports a subset of data from a relational database.

Inspired by [copyql](https://github.com/dolfelt/copyql). ❤️

## Installation

Use [pip](https://pip.pypa.io/en/stable/installing/).

```sh
pip install pycopyql
```

## Usage

```sh
pycopyql [-h] [-c CONFIG] [-f FORMAT] connection query [query ...]
```

* `-h`: Shows usage information
* `-c`: Path to a configuration file, defaults to `./pycopyql.py`
* `-f`: Output format, `sql` and `json` are supported, defaults to `sql`
* `connection`: Name of the connection to use, defined in the configuration file
* `query`: One or more query strings (delimited by spaces) of the format `TABLE.COLUMN:VALUE` (e.g. `accounts.id:1`)

Example:

```sh
pycopyql -c ./path/to/pycopyql.py -f json my_connection accounts.id:1 users.id:2
```

## Configuration

`pycopyql` uses a Python file for configuration. It looks like this.

```python
# pycopyql.py

config = {
    'connections': {
        'my_connection': {
            'drivername': 'mysql+mysqlconnector',
            'username': 'myuser',
            'password': 'mypassword',
            'host': 'localhost',
            'port': 3306,
            'database': 'mydatabase',
        }
    }
}
```

The file must define a `config` variable that is assigned a [dictionary](https://docs.python.org/3/tutorial/datastructures.html#dictionaries). That dictionary must have a `'connections'` key that is likewise assigned a dictionary.

Within `'connections'`, each key-value pair represents the configuration for a single database connection. The key is a name used to reference the connection when invoking `pycopyql`.

Under the hood, `pycopyql` uses the popular [SQLAlchemy library](http://www.sqlalchemy.org). Most settings for each connection correspond to the settings used for [SQLAlchemy URLs](http://docs.sqlalchemy.org/en/latest/core/engines.html#sqlalchemy.engine.url.URL).

### Resolvers

A **resolver** in `pycopyql` is a function that receives the names of a table and a column contained in that table and returns a list of table-column pairs related to the specified table-column pair that `pycopyql` will then search for data to include in its output.

Let's take a look at an example of a resolver that's bundled with `pycopyql`.

```
❯ python3
Python 3.7.0 (default, Jun 29 2018, 20:14:27)
[Clang 9.0.0 (clang-900.0.39.2)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> from pycopyql.resolver.inflector import dependents_inflector
>>> help(dependents_inflector)

Help on function dependents_inflector in module pycopyql.resolver.inflector:

dependents_inflector(meta, table, column)
    Uses inflection of column names to return foreign keys from tables that reference the specified column if it is a primary key.

    Parameters:
        meta (sqlalchemy.schema.MetaData): Metadata for the database structure
        table (string): Name of the table containing the column being examined
        column (string): Name of the column being examined

    Returns:
        list: List of dictionaries each containing the table and column of foreign key columns that reference the specified column
```

Let's assume that we're using this resolver with a database that looks like this.

```
+-----------+     +------------+     +---------+
| libraries <--+  | books      |  +--> authors |
+-----------+  |  +------------+  |  +---------+
| id        |  |  | id         |  |  | id      |
| name      |  +--+ library_id |  |  | name    |
| owner     |     | title      |  |  +---------+
+-----------+     | author_id  +--+
                  +------------+
```

Given a table name of `'libraries'` and a column name of `'id'`, `dependents_inflector` would return this.

```python
[
    { 'table': 'books', 'column': 'library_id' },
]
```

`pycopyql.resolver.inflector` also includes another resolver called `dependencies_inflector`, which works in the opposite direction of `dependents_inflector`. That is, where `dependents_inflector` returns foreign keys that reference a primary key, `dependencies_inflector` returns the primary key corresponding to a foreign key.

Using the above database as an example again, given a table name of `'books'` and a column name of `'library_id'`, `dependencies_inflector` would return this.

```python
[
    { 'table': 'libraries', 'column': 'id' },
]
```

A custom resolver that handles both of these cases using the bundled resolvers shown above might look like this.

```python
# pycopyql.py

from pycopyql.resolver.inflector import dependents_inflector, dependencies_inflector

def my_resolver(meta, table, column):
    dependents = dependents_inflector(meta, table, column)
    dependencies = dependencies_inflector(meta, table, column)
    return dependents + dependencies

config = {
    'connections': {
        'my_connection': {
            # SQLAlchemy connection parameters go here

            'resolver': my_resolver,
        },
    },
}
```

In fact, `pycopyql.resolver.inflector` contains yet another resolver called `inflector` that functions exactly this way.

Custom resolvers can operate in many ways. For example, one might use foreign keys to determine relationships. The `dependents_foreign_key` and `dependencies_foreign_key` resolvers contained in `pycopyql.resolver.foreign_key` are equivalent to the `dependents_inflector` and `dependencies_inflector` resolvers described earlier. `pycopyql.resolver.foreign_key` also includes the `foreign_key` resolver, which is likewise equivalent to the `inflector` resolver described earlier.

For some cases where database column naming conventions are inconsistent, or where one table requires multiple references to another table (e.g. identifiers of the last users who created and updated a record), a resolver can use a static list of keys specific to that database. Here's an example using the database schema shown earlier.

```python
def my_resolver(meta, table, column):
    keys = {
        'libraries': {
            'id': [ { 'table': 'books', 'column': 'library_id' } ],
        },
        'books': {
            'library_id': [ { 'table': 'libraries', 'column': 'id' } ],
            'author_id': [ { 'table': 'authors', 'column': 'id' } ]
        },
        'authors': {
            'id': [ { 'table': 'books', 'column': 'author_id' } ],
        },
    }
    if table in keys and column in keys[table]:
        return keys[table][column]
    return []
```

`pycopyql.resolver.static` contains a convenience function, `static_map`, that takes in a dictionary like the one assigned to `keys` in the example above and returns a resolver that will use that static map in the same way.

```python
from pycopyql.resolver.static import static_map

keys = {
    'table_1': {
        'column_1': [
            { 'table': 'other_table_1', 'column': 'other_column_1' },
            { 'table': 'other_table_2', 'column': 'other_column_2' },
            # ...
        ]
    },
    'table_2': {
        # ...
    },
    # ...
}

config = {
    'connections': {
        'my_connection': {
            # ...

            'resolver': static_map(keys),
        },
    },
}
```

Custom resolvers can use several of the resolvers described here together simultaneously. For example, if you wish to use inflection, but have some cases for which you must provide a static mapping, you can do both using a custom resolver.

```python
from pycopyql.resolver.inflector import inflector
from pycopyql.resolver.static import static_map

static_keys = {
    # ...
}

static_resolver = static_map(static_keys)

def my_resolver(meta, table, column):
    static = static_resolver(meta, table, column)
    inflected = inflector(meta, table, column)
    return static + inflected
```

## Output Formats

By default, `pycopyql` supports `sql` and `json` output formats. You can add additional formats or replace the bundled export functions for supported formats with your own.

In your configuration file, on the same level as the `'connections'` key, add an `'exporters'` key. The corresponding value should be a dictionary keyed by a format name that will be passed to `pycopyql` using its `-f` flag. The value should be a function that outputs given data in that format.

Let's take a look at one of the bundled export functions.

```
❯ python3
Python 3.7.0 (default, Jun 29 2018, 20:14:27)
[Clang 9.0.0 (clang-900.0.39.2)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> from pycopyql.export import export_sql
>>> help(export_sql)

Help on function export_sql in module pycopyql.export:

export_sql(meta, data)
    Outputs data as SQL INSERT statements.

    Parameters:
        meta (sqlalchemy.schema.MetaData): Metadata for the database structure
        data: Dictionary keyed by table name of dictionaries corresponding to table rows

    Returns:
        None
```

If you wanted to override the bundled SQL exporter, here's what it might look like.

```python
def my_sql_exporter(meta, data):
    # ...

config = {
    'connections': {
        # ...
    },
    'exporters': {
        'sql': my_sql_exporter,        
    },
}
```

## License

[MIT License](https://en.wikipedia.org/wiki/MIT_License)
