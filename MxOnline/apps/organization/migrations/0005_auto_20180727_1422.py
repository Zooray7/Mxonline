# Generated by Django 2.0.2 on 2018-07-27 06:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0004_teacher_img'),
    ]

    operations = [
        migrations.RenameField(
            model_name='teacher',
            old_name='img',
            new_name='image',
        ),
    ]