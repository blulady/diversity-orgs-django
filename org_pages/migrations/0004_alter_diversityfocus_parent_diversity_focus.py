# Generated by Django 4.0.4 on 2022-05-27 23:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('org_pages', '0003_remove_diversityfocus_parent_diversity_focus_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diversityfocus',
            name='parent_diversity_focus',
            field=models.ManyToManyField(blank=True, to='org_pages.diversityfocus'),
        ),
    ]
