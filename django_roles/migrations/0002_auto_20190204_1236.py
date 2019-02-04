# Generated by Django 2.0.7 on 2019-02-04 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_roles', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='templateaccess',
            name='flag',
            field=models.CharField(default=None, help_text='Flag is used with template tag check_role to restrict access in templates.', max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='templateaccess',
            name='roles',
            field=models.ManyToManyField(help_text='Select the groups (roles) with access with check_role template tag and flag.', related_name='template_access', to='auth.Group'),
        ),
        migrations.AlterField(
            model_name='viewaccess',
            name='roles',
            field=models.ManyToManyField(help_text='Select the groups (roles) with view access if access type = By role.', related_name='view_access', to='auth.Group'),
        ),
        migrations.AlterField(
            model_name='viewaccess',
            name='type',
            field=models.CharField(choices=[('pu', 'Public'), ('au', 'Authorized'), ('br', 'By role')], default=None, help_text='Type of access for the view. Select from available options.', max_length=2),
        ),
        migrations.AlterField(
            model_name='viewaccess',
            name='view',
            field=models.CharField(default=None, help_text='View name to be secured: <em>namespace:view_name</em>', max_length=255, unique=True),
        ),
    ]
