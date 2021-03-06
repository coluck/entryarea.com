# Generated by Django 2.2.2 on 2019-06-30 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=30)),
                ('slug', models.SlugField(blank=True, max_length=35, unique=True)),
                ('descr', models.CharField(blank=True, max_length=100)),
                ('lang', models.CharField(choices=[('en', 'English'), ('tr', 'Turkish')], max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('title', models.CharField(max_length=64)),
                ('lang', models.CharField(choices=[('en', 'English'), ('tr', 'Turkish')], max_length=2)),
                ('slug', models.SlugField(blank=True, max_length=100, null=True, unique=True)),
                ('views', models.PositiveIntegerField(default=0)),
                ('is_closed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('last_entry', models.DateTimeField(blank=True, null=True)),
                ('tags', models.ManyToManyField(blank=True, related_name='threads', to='threads.Tag')),
            ],
            options={
                'ordering': ['-last_entry'],
            },
        ),
    ]
