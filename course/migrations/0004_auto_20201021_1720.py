# Generated by Django 2.2.11 on 2020-10-21 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0003_auto_20200917_1644'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='remarks',
            field=models.CharField(max_length=100, null=True, verbose_name='备注'),
        ),
    ]
