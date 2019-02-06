"""
Code used by checkviewaccess management command
"""


def walk_site_url(_url_patterns, recursive_url=''):
    result = []
    for url in _url_patterns:
        if hasattr(url, 'pattern'):
            # Running With Django 2
            pattern = url.pattern
        else:
            # Running with Django 1
            pattern = url.regex.pattern
        pattern = pattern.strip('^')
        if hasattr(url, 'url_patterns'):
            result.extend(walk_site_url(url.url_patterns,
                                        recursive_url + pattern))
        else:
            result.append((recursive_url + pattern, url.callback))
    return result


# def walk_url_conf(urlpatterns, namespace=''):
#     for element in urlpatterns:
#         django_version = False
#         try:
#             django_version = isinstance(element, URLResolver)
#         except:
#             django_version = isinstance(element, RegexURLResolver)
#         if django_version:
#             walk_url_conf(element.url_patterns, namespace +
#                           element.regex.pattern)
#         else:
#             print(element.name)
#             print(namespace + element.regex.pattern)
#             # print(element.callback)
#             if hasattr(element.callback, 'access_by_role'):
#                 print("Protected View")