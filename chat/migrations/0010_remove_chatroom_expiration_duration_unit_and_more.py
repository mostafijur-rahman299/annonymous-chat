# Generated by Django 4.2.3 on 2024-12-26 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0009_alter_chatroom_expiration_duration_unit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatroom',
            name='expiration_duration_unit',
        ),
        migrations.AlterField(
            model_name='chatroom',
            name='expiration_duration',
            field=models.IntegerField(default=10),
        ),
    ]
