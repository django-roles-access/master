"""
Code used by checkviewaccess management command
"""


def walk_site_url(_url_patterns, recursive_url=''):
    """

    :param _url_patterns:
    :param recursive_url:
    :return: A list of tuples: (url, callback view, foo:view_name, app_name)
    """
    result = []
    for url in _url_patterns:
        if hasattr(url, 'pattern'):
            # Running With Django 2
            pattern = url.pattern
        else:
            # Running with Django 1
            pattern = url.regex.pattern
        pattern = pattern.strip('^')  # For better presentation
        if hasattr(url, 'url_patterns'):
            # When url object has 'url_patterns' attribute means is a Resolver
            result.extend(walk_site_url(url.url_patterns,
                                        recursive_url + pattern))
        else:
            result.append((recursive_url + pattern, url.callback))
    return result
