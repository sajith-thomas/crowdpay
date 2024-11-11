# Generated by Django 5.1.2 on 2024-11-10 16:46

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0011_transaction'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='payment',
            options={},
        ),
        migrations.RemoveField(
            model_name='payment',
            name='anonymous',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='email',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='name',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='phone',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='transaction_time',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='image',
        ),
        migrations.AddField(
            model_name='payment',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_method',
            field=models.CharField(blank=True, choices=[('stripe', 'Stripe'), ('razorpay', 'Razorpay')], max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='status',
            field=models.CharField(default='pending', max_length=20),
        ),
        migrations.AddField(
            model_name='payment',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='contributions',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='payment',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='payment',
            name='campaign',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.campaign'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='Transaction',
        ),
    ]
