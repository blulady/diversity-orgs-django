# Generated by Django 4.0.4 on 2022-05-28 00:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('org_pages', '0004_alter_diversityfocus_parent_diversity_focus'),
    ]

    operations = [
        migrations.AddField(
            model_name='diversityfocus',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]