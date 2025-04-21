from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Tag, Todo

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id', 'username', 'email']


class TodoSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, required=False)
    days_remaining = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Todo
        fields = [
            'id', 'title', 'description', 'due_date', 'priority', 'status',
            'created_at', 'updated_at', 'completed_at', 'user', 'tags',
            'days_remaining', 'is_overdue'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'completed_at', 'user'
        ]

    def get_days_remaining(self, obj):
        if obj.due_date:
            from django.utils import timezone
            remaining = obj.due_date - timezone.now()
            return remaining.days
        return None

    def get_is_overdue(self, obj):
        if obj.due_date and obj.status != 'completed':
            from django.utils import timezone
            return timezone.now() > obj.due_date
        return False

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        todo = Todo.objects.create(**validated_data)

        for tag_data in tags_data:
            tag, _ = Tag.objects.get_or_create(
                name=tag_data['name'], defaults=tag_data)
            todo.tags.add(tag)

        return todo

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)

        if tags_data is not None:
            instance.tags.clear()
            for tag_data in tags_data:
                tag, _ = Tag.objects.get_or_create(
                    name=tag_data['name'], defaults=tag_data)
                instance.tags.add(tag)

        return super().update(instance, validated_data)


class TodoStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ['status']

    def validate_status(self, value):
        if value not in dict(self.instance.STATUS_CHOICES).keys():
            raise serializers.ValidationError("Invalid status")
        return value


class TodoAttachmentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(use_url=True)

    class Meta:
        model = TodoAttachment
        fields = ['id', 'file', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class TodoDetailSerializer(TodoSerializer):
    attachments = TodoAttachmentSerializer(many=True, read_only=True)

    class Meta(TodoSerializer.Meta):
        fields = TodoSerializer.Meta.fields + ['attachments']
