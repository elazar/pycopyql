def static_map(keys):
    """
    Returns a resolver that uses a static map to determine which keys are related to the specified column.

    Parameters:
        keys (dict): Dictionary keyed by table name of dictionaries keyed by column name each containing a list of related columns

    Returns:
        function: Resolver callback
    """

    def resolver(meta, table, column):
        if table in keys and column in keys[table]:
            return keys[table][column]
        return []
    return resolver
