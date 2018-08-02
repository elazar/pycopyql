from .args import get_args
from .config import get_config, get_connection_config, get_engine, get_meta
from .query import query
from .export import get_exporter

def main():
    """
    Provides a CLI entrypoint to access a database and export a subset of its
    data in a specified format.
    """

    args = get_args()
    config = get_config(args.config)
    connection_config = get_connection_config(config, args.connection)
    engine = get_engine(connection_config)
    export = get_exporter(args.format, config['exporters'])

    connection = engine.connect()
    meta = get_meta(engine)
    resolver = connection_config['resolver']
    data = query(connection, meta, resolver, args.query)
    export(meta, data)
