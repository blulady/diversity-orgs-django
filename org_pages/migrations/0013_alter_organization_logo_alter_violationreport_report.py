# Generated by Django 4.0.4 on 2022-06-27 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('org_pages', '0012_alter_organization_code_of_conduct_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='logo',
            field=models.ImageField(blank=True, help_text="Logo of the organization. Will be displayed on the organization's page.", upload_to='media/logos/58afd7c2-81f4-4333-96fb-9a15856224bf/'),
        ),
        migrations.AlterField(
            model_name='violationreport',
            name='report',
            field=models.TextField(help_text='Report of the violation.'),
        ),
    ]