# Generated by Django 5.0 on 2023-12-13 09:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_remove_customuser_content_comment_like'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='content',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_content', to='app.content'),
        ),
    ]
