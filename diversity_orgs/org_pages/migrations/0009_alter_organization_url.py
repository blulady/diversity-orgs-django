# Generated by Django 4.0.4 on 2022-05-25 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('org_pages', '0008_alter_location_location_alter_organization_location_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='url',
            field=models.URLField(blank=True, null=True),
        ),
    ]