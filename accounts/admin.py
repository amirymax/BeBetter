from django.contrib import admin
from .models import Level, Task, CompletedTask, Category

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'level_type']
    list_filter = ['level_type']  # Добавляем фильтр по типу уровня
    search_fields = ['name', 'description']  # Поля для поиска

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['description', 'level', 'category', 'resource_link']
    list_filter = ['level', 'category']
    search_fields = ['description']

@admin.register(CompletedTask)
class CompletedTaskAdmin(admin.ModelAdmin):
    list_display = ['task', 'level',  'user']