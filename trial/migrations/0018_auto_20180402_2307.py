# Generated by Django 2.0.3 on 2018-04-02 20:07

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('trial', '0017_auto_20180330_1740'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='doctor_fk',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='trial.Doctor'),
        ),
        migrations.AlterField(
            model_name='globalchecker',
            name='last_checked',
            field=models.DateTimeField(default=datetime.datetime(2018, 4, 2, 20, 7, 54, 737057, tzinfo=utc)),
        ),
    ]
