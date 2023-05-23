# Generated by Django 4.0.4 on 2022-07-01 14:41

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('org_pages', '0019_organization_social_links_alter_organization_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='diversityfocus',
            name='other_names',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='organization',
            name='logo',
            field=models.ImageField(blank=True, help_text="Logo of the organization. Will be displayed on the organization's page.", upload_to='media/logos/1eff6117-9933-4a0f-9c37-8ae4bf3ea36b/'),
        ),
    ]