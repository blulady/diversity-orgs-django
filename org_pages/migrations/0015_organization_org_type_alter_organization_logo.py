# Generated by Django 4.0.4 on 2022-06-29 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('org_pages', '0014_alter_organization_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='org_type',
            field=models.CharField(blank=True, choices=[('USER_GROUP', 'User Group'), ('EMPLOYMENT ASSISTANCE PROGRAM', 'Employment Assistance Program'), ('NETWORKING', 'Network'), ('MENTORSHIP', 'Mentorship'), ('CONFERENCE', 'Conference'), ('YOUTH ORGANIZATION', 'Youth Organization'), ('OTHER', 'Other')], default='USER_GROUP', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='organization',
            name='logo',
            field=models.ImageField(blank=True, help_text="Logo of the organization. Will be displayed on the organization's page.", upload_to='media/logos/db005657-15be-45e0-a5ac-1f59921db9ea/'),
        ),
    ]