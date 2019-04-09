# Django roles Change Log

## [0.8.6] - 2019-04-09 Release candidate

### Added

- Action checkviewaccess report output with csv format.

- New documentation title: [Test coverage](https://django-roles-access.github.io/coverage.html)

## [0.8.5] - 2019-04-03

### Changed

- Better look & feel in README.md file.

## [0.8.4] - 2019-04-03

### Changed

- Unify README file in one README.md file. 

- setup.py now got a new property long_description_content_type equal to
  'text/markdown' letting markdown in Pypi.

## [0.8.3] - 2019-03-22

### Changed

- Documentation move it to: [Django roles access](https://django-roles-access.github.io)

- README file for Pypi.org.

- README.rst file for Github.com adding reference to Pypi.org and Travis

### Added

- Configuration and integration with Travis-CI.org.

## [0.8.2] - 2019-03-21

### Changed

- License update to MIT LICENSE.

## [0.8.1]  - 2019-03-19

### Added

- Updates in config file for updating to Pypi.org.

## [0.8] - 2019-03-19

### Changed
- As the name is already used at Pypi.org (`django-roles`), it is changed to 
the new name `django-roles-access`.

## [0.7] - 2019-03-15

### Added
**Implement enhancements:**

- Start change log file.

- Add new configuration attribute **DJANGO_ROLES_FORBIDDEN_MESSAGE**. If not 
defined default value is: `'<h1>403 Forbidden</h1>'`

- Add new configuration attribute **DJANGO_ROLES_REDIRECT**. Default behavior
 when attribute has not been set, or is False, and user has no access 
 permission to the view: a 
 *django.http.HttpResponseForbidden(DJANGO_ROLES_FORBIDDEN_MESSAGE)* is 
 returned. When DJANGO_ROLES_REDIRECT is True what is returned is a
 *django.http.HttpResponseRedirect(settings.LOGIN_URL)

### Changed

- Change default behavior of raising PermissionDenied when user has no access
 permission to the view. No more PermissionDenied is raised (see Added).
