# Generated by Django 2.1.1 on 2018-09-01 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='description',
            field=models.TextField(blank=True, max_length=300),
        ),
    ]
