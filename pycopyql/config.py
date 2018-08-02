from os.path import abspath
from importlib.util import spec_from_file_location, module_from_spec
from sqlalchemy import create_engine, MetaData
from sqlalchemy.engine.url import URL

def get_config(file):
    """
    Imports configuration from a Python file.

    Parameters:
        string: Path to the file

    Returns:
        dict: 'config' variable imported from the file
    """

    path = abspath(file)

    # Check that the file exists, throw an error if it doesn't
    with open(path) as fh:
        pass

    spec = spec_from_file_location('config', path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    config = module.config

    if not config['connections'] or type(config['connections']) != dict:
        raise RuntimeError('config must have a connections property containing a dict')

    if not 'exporters' in config:
        config['exporters'] = []
    else:
        for name, exporter in config['exporters']:
            if type(exporter) != function:
                raise RuntimeError('exporter %s is not a function' % name)

    return config

def get_connection_config(configuration, connection):
    """
    Extracts information for a specified connection from configuration.

    Parameters:
        configuration (dict): Configuration dictionary containing a 'connections' key
        connection (string): Name of a connection to extract configuration for

    Returns:
        dict: Configuration associated with the specified connection
    """

    if not connection in configuration['connections']:
        raise RuntimeError('connection "%s" not found in config.connections' % connection)
    return configuration['connections'][connection]

def get_engine(engine_config):
    """
    Initializes a SQLAlchemy engine using provided configuration.

    Parameters:
        engine_config (dict): Engine configuration, see http://docs.sqlalchemy.org/en/latest/core/engines.html#sqlalchemy.create_engine

    Returns:
        sqlalchemy.engine.Engine: Configured engine
    """

    url_fields = (
        'drivername',
        'username',
        'password',
        'host',
        'port',
        'database',
    )
    url_params = dict((key, engine_config[key]) for key in url_fields if key in engine_config)
    url = URL(**url_params)
    return create_engine(url)

def get_meta(engine):
    """
    Returns structural metadata for the database being accessed.

    Parameters:
        engine (sqlalchemy.engine.Engine): Engine to which the metadata object will be bound
        
    Returns:
        sqlalchemy.schema.MetaData: Loaded database table definitions
    """

    meta = MetaData(bind=engine)
    meta.reflect()
    return meta
