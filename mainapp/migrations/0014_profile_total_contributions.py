# Generated by Django 5.1.2 on 2024-11-10 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0013_alter_payment_campaign'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='total_contributions',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
