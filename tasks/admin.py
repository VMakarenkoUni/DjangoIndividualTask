from django.contrib import admin
from .models import Project, Task

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'status', 'parent_task', 'created_at', 'updated_at')
    list_filter = ('status', 'project')
    search_fields = ('title', 'description')
    # Для зручного редагування ієрархії можна додати raw_id_fields для parent_task
    raw_id_fields = ('parent_task',)