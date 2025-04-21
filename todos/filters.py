import django_filters
from django.db import models

from .models import Todo


class TodoFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    priority = django_filters.NumberFilter()
    priority__gt = django_filters.NumberFilter(
        field_name='priority', lookup_expr='gt')
    priority__lt = django_filters.NumberFilter(
        field_name='priority', lookup_expr='lt')
    status = django_filters.CharFilter(lookup_expr='iexact')
    due_date = django_filters.DateTimeFilter()
    due_date__gt = django_filters.DateTimeFilter(
        field_name='due_date', lookup_expr='gt')
    due_date__lt = django_filters.DateTimeFilter(
        field_name='due_date', lookup_expr='lt')
    tags = django_filters.CharFilter(
        field_name='tags__name', lookup_expr='iexact')

    class Meta:
        model = Todo
        fields = {
            'title': ['exact', 'icontains'],
            'priority': ['exact', 'gt', 'lt'],
            'status': ['exact'],
            'due_date': ['exact', 'gt', 'lt'],
        }

    order_by = django_filters.OrderingFilter(
        fields=(
            ('priority', 'priority'),
            ('due_date', 'due_date'),
            ('created_at', 'created_at'),
            ('updated_at', 'updated_at'),
        )
    )
