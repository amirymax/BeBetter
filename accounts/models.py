from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    CATEGORY_CHOICES = [
        ('science', 'Наука'),
        ('art', 'Искусство'),
        ('health', 'Медицина'),
        ('sport', 'Спорт'),
        ('it', 'IT'),
        ('business', 'Бизнес'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    level = models.IntegerField(default=1)
    completed_tasks = models.IntegerField(default=0)
    current_task = models.CharField(max_length=255, default="", blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='science')

    def __str__(self):
        return self.user.username

class Level(models.Model):
    LEVEL_TYPES = [
        ('mental', 'Ментальный'),
        ('physical', 'Физический'),
    ]

    name = models.CharField(max_length=50)  # Название уровня
    description = models.TextField(blank=True)  # Описание уровня
    level_type = models.CharField(max_length=10, choices=LEVEL_TYPES, default='mental')  # Тип уровня

    def __str__(self):
        return f"{self.name} ({self.get_level_type_display()})"


class Category(models.Model):
    name = models.CharField(max_length=50)  # Название категории (например, "Наука", "Искусство")

    def __str__(self):
        return self.name


class Task(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='tasks')  # Привязка задачи к уровню
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='tasks')  # Привязка к категории
    description = models.CharField(max_length=255)  # Описание задачи
    resource_link = models.URLField(blank=True, null=True)  # Ссылка на ресурс (статья/книга)

    def __str__(self):
        return f"{self.description} ({self.category.name})"

class CompletedTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.CharField(max_length=255)
    level = models.IntegerField()

    def __str__(self):
        return f"{self.task} (Level {self.level})"