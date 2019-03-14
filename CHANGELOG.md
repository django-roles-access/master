# Django roles Change Log

## [0.7] - 2019-03-14

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
