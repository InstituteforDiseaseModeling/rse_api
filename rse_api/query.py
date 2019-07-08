from flask import request


def get_pagination_from_request(page_default: int = 1, per_page_default: int = 100) -> dict:
    """
    Returns the pagination filter created from a request

    Page is assumed to be in the `page` query parameters
    The number of items per page is assumed to be in the per_page query option

    The turns will be a dictionary container the values for page and per_page. If no values were passed to the request
    the values will be defaults of page_default and per_page_default
    Args:
        page_default: Page default if not present in request
        per_page_default:  PerPage default if not present in request

    Returns:

    """
    options = dict(page=request.args.get('page', page_default),
                   per_page=request.args.get('per_page', per_page_default)
                   )
    for k in options.keys():
        if isinstance(options[k], str):
            options[k] = int(options[k])
    return options
