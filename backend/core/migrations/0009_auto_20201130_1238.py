# Generated by Django 3.1.3 on 2020-11-30 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20201130_1148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='recorded_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
