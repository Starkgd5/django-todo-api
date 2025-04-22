import redis
from django.conf import settings
from django.db import connection
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (OpenApiExample, OpenApiParameter,
                                   extend_schema)
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import TodoFilter
from .models import Tag, Todo
from .serializers import (TagSerializer, TodoAttachmentSerializer,
                          TodoDetailSerializer, TodoSerializer,
                          TodoStatusUpdateSerializer)
from .throttles import BurstRateThrottle, SustainedRateThrottle


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Test database connection
        try:
            connection.ensure_connection()
            db_status = 'up'
        except Exception:
            db_status = 'down'

        # Test cache connection
        try:
            cache = redis.Redis.from_url(
                settings.CACHES['default']['LOCATION'])
            cache.ping()
            cache_status = 'up'
        except Exception:
            cache_status = 'down'

        return Response({
            'status': 'up',
            'components': {
                'database': db_status,
                'cache': cache_status
            }
        })


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return self.queryset.filter(todos__user=self.request.user).distinct()


class TodoViewSet(viewsets.ModelViewSet):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TodoFilter
    search_fields = ['title', 'description']
    ordering_fields = ['priority', 'due_date', 'created_at', 'updated_at']
    if settings.DJANGO_SETTINGS_MODULE == 'core.settings.production':
        throttle_classes = [BurstRateThrottle, SustainedRateThrottle]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).select_related('user').prefetch_related('tags')

    @method_decorator(cache_page(60 * 15))
    @method_decorator(vary_on_cookie)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['patch'], serializer_class=TodoStatusUpdateSerializer)
    def update_status(self, request, pk=None):
        todo = self.get_object()
        serializer = self.get_serializer(todo, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def completed(self, request):
        completed_todos = self.get_queryset().filter(status='completed')
        page = self.paginate_queryset(completed_todos)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(completed_todos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        overdue_todos = self.get_queryset().filter(
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        )
        page = self.paginate_queryset(overdue_todos)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(overdue_todos, many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TodoDetailSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=['post'], serializer_class=TodoAttachmentSerializer)
    def upload_attachment(self, request, pk=None):
        todo = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(todo=todo)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
