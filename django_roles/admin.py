# encoding='utf-8'

from django.contrib import admin

from django_roles.models import ViewAccess, TemplateAccess


# admin.site.register(ViewAccess, ViewAccessAdmin)
admin.site.register(ViewAccess)
admin.site.register(TemplateAccess)
