def get_uri_filter(app):
    """
    Return a filter function that takes a URI and returns whether it should
    be filter out from the swagger documentation or not.

    Arguments:
        app: The application to take `config.API_URI_FILTER` from. Possible
             values for this config option are: `slash` (to keep URIs that
             end with a `/`), `all` (to keep all URIs). All other values
             default to keep all URIs that don't end with a `/`.

    Returns:
        `True` if the URI should be *filtered out* from the swagger
        documentation, and `False` if it should be kept in the documentation.
    """
    choice = getattr(app.config, "API_URI_FILTER", None)

    if choice == "slash":
        # Keep URIs that end with a /.
        return lambda uri: not uri.endswith("/")

    if choice == "all":
        # Keep all URIs.
        return lambda uri: False

    # Keep URIs that don't end with a /, (special case: "/").
    return lambda uri: len(uri) > 1 and uri.endswith("/")


def remove_nulls(dictionary, deep=True):
    """
    Removes all null values from a dictionary.
    """
    return {k: remove_nulls(v, deep) if deep and type(v) is dict else v for k, v in dictionary.items() if v is not None}
