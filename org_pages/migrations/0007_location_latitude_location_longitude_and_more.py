# Generated by Django 4.0.4 on 2022-06-01 23:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('org_pages', '0006_alter_location_options_organization_logo_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=5, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=5, max_digits=9, null=True),
        ),
        migrations.AlterField(
            model_name='parentorganization',
            name='logo',
            field=models.ImageField(blank=True, upload_to='media/logos/1cf9ab7b-e663-4c96-8a83-9d358adfedb8/'),
        ),
    ]