# Generated by Django 3.1.5 on 2021-01-21 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Song',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('song', models.CharField(max_length=100)),
                ('artist', models.CharField(max_length=100)),
                ('url', models.URLField(max_length=300)),
                ('valence', models.DecimalField(decimal_places=4, max_digits=7)),
                ('energy', models.DecimalField(decimal_places=4, max_digits=7)),
                ('danceability', models.DecimalField(decimal_places=4, max_digits=7)),
            ],
        ),
    ]
