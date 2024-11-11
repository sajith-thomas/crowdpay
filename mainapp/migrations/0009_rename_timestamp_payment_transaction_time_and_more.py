# Generated by Django 5.1.2 on 2024-11-05 18:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0008_payment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='timestamp',
            new_name='transaction_time',
        ),
        migrations.AddField(
            model_name='payment',
            name='anonymous',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='payment',
            name='currency',
            field=models.CharField(default='INR', max_length=10),
        ),
        migrations.AddField(
            model_name='payment',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='amount',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='payment',
            name='campaign',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.campaign'),
        ),
    ]