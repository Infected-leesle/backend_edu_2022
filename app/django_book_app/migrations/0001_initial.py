# Generated by Django 4.0.3 on 2022-03-20 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(blank=True)),
                ('author', models.CharField(blank=True, max_length=40)),
                ('pub_year', models.DecimalField(decimal_places=0, max_digits=4)),
                ('price', models.DecimalField(decimal_places=3, max_digits=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
