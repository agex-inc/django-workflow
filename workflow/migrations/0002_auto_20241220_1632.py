# Generated by Django 2.2.13 on 2024-12-20 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='onapprovedhook',
            name='hook_type',
            field=models.CharField(choices=[('BEFORE', 'Before'), ('AFTER', 'After')], max_length=50, verbose_name='When?'),
        ),
        migrations.AlterField(
            model_name='oncompletehook',
            name='hook_type',
            field=models.CharField(choices=[('BEFORE', 'Before'), ('AFTER', 'After')], max_length=50, verbose_name='When?'),
        ),
        migrations.AlterField(
            model_name='ontransithook',
            name='hook_type',
            field=models.CharField(choices=[('BEFORE', 'Before'), ('AFTER', 'After')], max_length=50, verbose_name='When?'),
        ),
        migrations.AlterField(
            model_name='transition',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('cancelled', 'Cancelled'), ('done', 'Done'), ('jumped', 'Jumped')], default='pending', max_length=100, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='transitionapproval',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('cancelled', 'Cancelled'), ('jumped', 'Jumped')], default='pending', max_length=100, verbose_name='Status'),
        ),
    ]
