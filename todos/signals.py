from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Todo


@receiver(post_save, sender=Todo)
def send_todo_notification(sender, instance, created, **kwargs):
    if created:
        subject = f'New Todo Created: {instance.title}'
        message = f'You have created a new todo:\n\nTitle: {instance.title}\nPriority: {instance.get_priority_display()}\nDue Date: {instance.due_date}'
        send_mail(
            subject,
            message,
            'todos@example.com',
            [instance.user.email],
            fail_silently=False,
        )
    elif instance.status == 'completed':
        subject = f'Todo Completed: {instance.title}'
        message = f'Congratulations! You have completed the todo:\n\nTitle: {instance.title}'
        send_mail(
            subject,
            message,
            'todos@example.com',
            [instance.user.email],
            fail_silently=False,
        )
