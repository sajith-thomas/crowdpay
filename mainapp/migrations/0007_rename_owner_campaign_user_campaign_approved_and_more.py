# Generated by Django 5.1.2 on 2024-10-31 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0006_profile'),
    ]

    operations = [
        migrations.RenameField(
            model_name='campaign',
            old_name='owner',
            new_name='user',
        ),
        migrations.AddField(
            model_name='campaign',
            name='approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='goal',
            field=models.DecimalField(decimal_places=2, help_text='Enter amount in rupees', max_digits=10),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='title',
            field=models.CharField(max_length=255),
        ),
    ]