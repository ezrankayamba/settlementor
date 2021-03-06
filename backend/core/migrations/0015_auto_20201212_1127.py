# Generated by Django 3.1.3 on 2020-12-12 08:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20201209_1123'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fileentry',
            options={'verbose_name_plural': 'File entries'},
        ),
        migrations.AddField(
            model_name='payment',
            name='file_entry',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='core.fileentry'),
        ),
    ]
