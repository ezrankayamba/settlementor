# Generated by Django 3.1.3 on 2020-11-10 16:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20201110_1832'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentfile',
            name='consumer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='core.consumer'),
        ),
    ]
