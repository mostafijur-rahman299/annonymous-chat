# Generated by Django 4.2.3 on 2024-12-26 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0010_remove_chatroom_expiration_duration_unit_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatroom',
            name='expiration_duration',
            field=models.IntegerField(blank=True, default=10, null=True),
        ),
    ]