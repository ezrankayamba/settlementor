# Generated by Django 3.1.3 on 2021-02-17 06:30

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20201212_1658'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='consumer',
            options={'ordering': ['-recorded_at']},
        ),
        migrations.AlterModelOptions(
            name='customer',
            options={'ordering': ['-recorded_at']},
        ),
        migrations.AlterModelOptions(
            name='fileentry',
            options={'ordering': ['-recorded_at'], 'verbose_name_plural': 'File entries'},
        ),
        migrations.AlterModelOptions(
            name='payment',
            options={'ordering': ['-recorded_at']},
        ),
        migrations.AddField(
            model_name='consumer',
            name='recorded_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='consumer',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='fileentry',
            name='recorded_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fileentry',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='recorded_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='payment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
