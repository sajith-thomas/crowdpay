# Generated by Django 5.1.2 on 2024-11-10 16:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0012_alter_payment_options_remove_payment_anonymous_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='campaign',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.campaign'),
        ),
    ]
