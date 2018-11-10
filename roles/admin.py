# encoding='utf-8'

from django.contrib import admin

from roles.models import ViewAccess, TemplateAccess
from roles.utils import get_view_names_choices


# Register your models here.
class ViewAccessAdmin(admin.ModelAdmin):
    """
    Used to set an horizontal select style for the grops with access rights to the view.
    """
    filter_horizontal = ['roles']

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        """

        :param db_field:
        :param request:
        :param kwargs:
        :return:
        """
        if db_field.name == 'url_name':
            if len(db_field.choices) <= 2:
                choices = db_field.choices
                choices += get_view_names_choices()
                kwargs['choices'] = choices
        return super(ViewAccessAdmin, self).formfield_for_choice_field(db_field, request, **kwargs)


admin.site.register(ViewAccess, ViewAccessAdmin)

admin.site.register(TemplateAccess)
