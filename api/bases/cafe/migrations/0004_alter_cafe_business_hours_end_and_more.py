# Generated by Django 4.1.7 on 2023-05-01 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cafe', '0003_alter_cafe_latitude_alter_cafe_longitude'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cafe',
            name='business_hours_end',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cafe',
            name='business_hours_start',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
