# Generated by Django 2.1 on 2018-08-23 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='TemplateAccess',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flag', models.CharField(max_length=255, unique=True)),
                ('roles', models.ManyToManyField(to='auth.Group')),
            ],
        ),
        migrations.CreateModel(
            name='ViewAccess',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('view', models.CharField(max_length=255, unique=True)),
                ('type', models.CharField(choices=[('pu', 'Public'), ('au', 'Authorized'), ('br', 'By role')], max_length=2)),
                ('roles', models.ManyToManyField(to='auth.Group')),
            ],
        ),
    ]
