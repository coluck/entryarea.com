# Generated by Django 2.1 on 2018-08-26 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('threads', '0004_auto_20180826_1151'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='thread',
            field=models.ManyToManyField(blank=True, related_name='tags', to='threads.Thread'),
        ),
    ]