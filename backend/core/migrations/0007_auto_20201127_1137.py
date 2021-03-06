# Generated by Django 3.1.3 on 2020-11-27 08:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20201110_1916'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(max_length=20, unique=True)),
                ('timestamp', models.CharField(max_length=40)),
                ('file_reference_id', models.CharField(max_length=20, unique=True)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=38)),
                ('count_of_records', models.IntegerField()),
                ('status', models.CharField(default='Pending', max_length=20)),
                ('entry_type', models.CharField(default='PAYMENT_FILE', max_length=20)),
                ('consumer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.consumer')),
            ],
        ),
        migrations.DeleteModel(
            name='PaymentFile',
        ),
    ]
