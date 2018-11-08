def register_api(view, endpoint, url=None, pk='id', pk_type='int', methods=['GET', 'PUT', 'DELETE', 'POST'], app=None):
    """
    Registers a class as an api endpoint

    :param view: The Class to register as api controller
    :param endpoint: Endpoint the class represents This will be used internally for naming the object
    :param url: Optional. Will be
    :param pk: Name of the id field for object in the url/ Defaults to id
    :param pk_type: The type of the id field. Default to int
    :param methods: HTTP Methods this controller supports. Default is GET, PUT, DELETE, POST. Get will be
    registered for to sets of urls. The unique object versions, ie /objects/id and the listing of all objects,
    ie /objects. POST will only be registered at the top level url is specified, ie /objects
    :param app: App object to register url
    :return: None
    """
    view_func = view.as_view(endpoint)
    if url is None:
        url = endpoint
    if url[0] != '/':
        url = '/' + url
    if url[-1] == '/':
        url = url[0:-1]

    if app is None:
        # We have to import here to avoid circular dependency at load time
        from rse_api import get_application
        app = get_application()
    # these are the main listing methods
    if 'GET' in methods:
        app.add_url_rule(url, strict_slashes=False, defaults={pk: None},
                         view_func=view_func, methods=['GET', ])
    if 'POST' in methods:
        app.add_url_rule(url, strict_slashes=False, view_func=view_func, methods=['POST', ])
    app.logger.info('Register URL %s/<%s:%s>' % (url, pk_type, pk))
    # ensure post is not a method at this point
    fm = [f for f in methods.copy() if f != 'POST']
    app.add_url_rule('%s/<%s:%s>' % (url, pk_type, pk), view_func=view_func,
                     methods=fm)
