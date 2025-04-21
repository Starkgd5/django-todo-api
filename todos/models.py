from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#FFFFFF')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Todo(models.Model):
    PRIORITY_CHOICES = [
        (1, _('Low')),
        (2, _('Medium')),
        (3, _('High')),
        (4, _('Critical')),
    ]

    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('archived', _('Archived')),
    ]

    title = models.CharField(max_length=200, verbose_name=_('Title'))
    description = models.TextField(
        blank=True, null=True, verbose_name=_('Description'))
    due_date = models.DateTimeField(
        blank=True, null=True, verbose_name=_('Due Date'))
    priority = models.IntegerField(
        choices=PRIORITY_CHOICES, default=2, verbose_name=_('Priority'))
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('Status'))
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_('Description'))
    completed_at = models.DateTimeField(
        blank=True, null=True, verbose_name=_('Description'))
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='todos', verbose_name=_('Description'))
    tags = models.ManyToManyField(
        Tag, related_name='todos', blank=True, verbose_name=_('Description'))

    class Meta:
        ordering = ['-priority', 'due_date']
        indexes = [
            models.Index(fields=['priority']),
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'completed' and self.completed_at:
            self.completed_at = None
        super().save(*args, **kwargs)


class TodoAttachment(models.Model):
    todo = models.ForeignKey(
        Todo, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='todo_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.todo.title}"
