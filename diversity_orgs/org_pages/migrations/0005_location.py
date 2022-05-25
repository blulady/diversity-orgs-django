# Generated by Django 4.0.4 on 2022-05-24 04:14

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('org_pages', '0004_alter_organization_diversity_focus_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('location', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('region', models.CharField(blank=True, max_length=250)),
                ('country', models.CharField(blank=True, max_length=250)),
            ],
        ),
    ]