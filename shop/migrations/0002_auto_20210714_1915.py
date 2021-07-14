# Generated by Django 3.2.5 on 2021-07-14 16:15

from django.db import migrations, models
import django.db.models.deletion
import shop.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='image',
            options={'ordering': ('content_type', 'tip')},
        ),
        migrations.RemoveField(
            model_name='image',
            name='feedback',
        ),
        migrations.RemoveField(
            model_name='image',
            name='product',
        ),
        migrations.AddField(
            model_name='image',
            name='content_type',
            field=models.ForeignKey(db_column='content_type_id', default=1, limit_choices_to=shop.models.content_type_choices, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='image',
            name='object_id',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]
