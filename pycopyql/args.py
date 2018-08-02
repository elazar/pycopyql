from argparse import ArgumentParser
import os

def get_args():
    """
    Parses arguments passed to the CLI tool.

    Returns:
        dict: Key-value pairs from parsed CLI arguments
    """

    parser = ArgumentParser()
    parser.add_argument(
        '-c', '--config',
        default=os.getcwd() + os.sep + 'pycopyql.py',
        help='Path to pycopyql.py configuration file, defaults to ./pycopyql.py',
    )
    parser.add_argument(
        '-f', '--format',
        default='sql',
        help='Output format, supported values are sql and json, defaults to sql',
    )
    parser.add_argument(
        'connection',
        help='Name of the database connection to use',
    )
    parser.add_argument(
        'query',
        nargs='+',
        help='Query of the form TABLE.COLUMN:VALUE',
    )
    return parser.parse_args()
