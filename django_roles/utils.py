"""
Code used by checkviewaccess management command
"""


def walk_site_url(_url_patterns, recursive_url='',
                  view_name=None, app_name=None):
    """

    :param _url_patterns:
    :param recursive_url:
    :param view_name:
    :param app_name:
    :return: A list of tuples: (url, callback view, foo:view_name, app_name)
    """
    result = []
    for url in _url_patterns:
        if hasattr(url, 'pattern'):
            # Running With Django 2
            pattern = str(url.pattern)
        else:
            # Running with Django 1
            pattern = str(url.regex.pattern)
        pattern = pattern.strip('^')  # For better presentation
        pattern = pattern.strip('$')  # For better presentation
        if hasattr(url, 'url_patterns'):
            # When url object has 'url_patterns' attribute means is a Resolver
            if view_name:
                new_view_name = view_name + ":" + url.namespace
            else:
                new_view_name = url.namespace
            result.extend(walk_site_url(url.url_patterns,
                                        recursive_url + pattern,
                                        new_view_name, url.app_name))
        else:
            if view_name:
                new_view_name = view_name + ":" + url.name
            else:
                new_view_name = url.name
            result.append((recursive_url + pattern, url.callback,
                           new_view_name, app_name))

    return result


def get_views_by_app():
    pass
