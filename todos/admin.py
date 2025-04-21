from django.contrib import admin
from django.utils.html import format_html

from .models import Tag, Todo


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_display', 'created_at')
    search_fields = ('name',)

    def color_display(self, obj):
        return format_html(
            '<span style="width:20px; height:20px; display:inline-block; background-color:{}"></span> {}',
            obj.color,
            obj.color
        )
    color_display.short_description = 'Color'


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'priority_display',
                    'status_display', 'due_date', 'created_at')
    list_filter = ('priority', 'status', 'user', 'tags')
    search_fields = ('title', 'description')
    filter_horizontal = ('tags',)
    readonly_fields = ('created_at', 'updated_at', 'completed_at')

    def priority_display(self, obj):
        colors = {
            1: 'green',
            2: 'blue',
            3: 'orange',
            4: 'red'
        }
        return format_html(
            '<span style="color:{}">{}</span>',
            colors.get(obj.priority, 'black'),
            obj.get_priority_display()
        )
    priority_display.short_description = 'Priority'

    def status_display(self, obj):
        colors = {
            'pending': 'gray',
            'in_progress': 'blue',
            'completed': 'green',
            'archived': 'black'
        }
        return format_html(
            '<span style="color:{}">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
