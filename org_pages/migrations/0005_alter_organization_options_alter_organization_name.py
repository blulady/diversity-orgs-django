# Generated by Django 4.0.4 on 2022-06-15 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('org_pages', '0004_alter_diversityfocus_options_alter_location_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='organization',
            options={'ordering': ('parent__exact', 'name')},
        ),
        migrations.AlterField(
            model_name='organization',
            name='name',
            field=models.CharField(max_length=200),
        ),
    ]