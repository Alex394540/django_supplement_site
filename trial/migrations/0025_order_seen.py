# Generated by Django 2.0.3 on 2018-04-05 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trial', '0024_remove_order_discount'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='seen',
            field=models.BooleanField(default=False),
        ),
    ]
