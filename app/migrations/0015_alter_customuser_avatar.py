# Generated by Django 5.0 on 2023-12-17 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_chat_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='avatar',
            field=models.ImageField(blank=True, default='default.jpg', null=True, upload_to='avatars/'),
        ),
    ]
