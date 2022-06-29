# Generated by Django 4.0.4 on 2022-06-29 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('org_pages', '0015_organization_org_type_alter_organization_logo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='logo',
            field=models.ImageField(blank=True, help_text="Logo of the organization. Will be displayed on the organization's page.", upload_to='media/logos/ff1cfc98-ef31-4eac-b6b8-5b21ed978cf6/'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='org_type',
            field=models.CharField(blank=True, choices=[('USER_GROUP', 'User Group'), ('EMPLOYMENT ASSISTANCE PROGRAM', 'Employment Assistance Program'), ('NETWORKING', 'Network'), ('MENTORSHIP', 'Mentorship'), ('CONFERENCE', 'Conference'), ('YOUTH ORGANIZATION', 'Youth Organization'), ('CODE SCHOOL', 'Code School'), ('OTHER', 'Other')], default='USER_GROUP', max_length=50, null=True),
        ),
    ]
