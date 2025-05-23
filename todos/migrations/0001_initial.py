# Generated by Django 5.2 on 2025-04-21 16:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('color', models.CharField(default='#FFFFFF', max_length=7)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Todo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('due_date', models.DateTimeField(blank=True, null=True)),
                ('priority', models.IntegerField(choices=[(1, 'Low'), (2, 'Medium'), (3, 'High'), (4, 'Critical')], default=2)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('archived', 'Archived')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('tags', models.ManyToManyField(blank=True, related_name='todos', to='todos.tag')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='todos', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-priority', 'due_date'],
                'indexes': [models.Index(fields=['priority'], name='todos_todo_priorit_93f987_idx'), models.Index(fields=['status'], name='todos_todo_status_9f7c48_idx'), models.Index(fields=['due_date'], name='todos_todo_due_dat_f2739d_idx')],
            },
        ),
    ]
