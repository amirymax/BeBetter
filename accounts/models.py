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

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    birth_date = models.DateField(null=True, blank=True)  # Поле даты рождения
    level = models.IntegerField(default=1)  # Текущий уровень
    completed_tasks = models.IntegerField(default=0)  # Количество завершённых заданий
    current_task_number = models.IntegerField(default=1)  # Номер текущего задания
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='science')  # Категория

    def __str__(self):
        return self.user.username

    def update_current_task(self):
        """Обновление номера текущего задания."""
        self.current_task_number = self.completed_tasks + 1
        self.save()
    
    class Meta:
        app_label = 'accounts'

class Level(models.Model):
    LEVEL_TYPES = [
        ('mental', 'Ментальный'),
        ('physical', 'Физический'),
    ]

    number = models.PositiveIntegerField(unique=True, editable=False)  # Номер уровня (по порядку)
    level_type = models.CharField(max_length=10, choices=LEVEL_TYPES, default='mental', editable=False)  # Тип уровня

    def save(self, *args, **kwargs):
        # Если номер уровня ещё не установлен, вычисляем его
        if not self.number:
            # Определяем следующий номер уровня
            last_level = Level.objects.all().order_by('number').last()
            self.number = (last_level.number + 1) if last_level else 1
            self.level_type = 'mental' if self.number % 2 == 1 else 'physical'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.number}"



class Category(models.Model):
    name = models.CharField(max_length=50)  # Название категории (например, "Наука", "Искусство")

    def __str__(self):
        return self.name


class Task(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='tasks')  # Привязка задачи к уровню
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='tasks')  # Привязка к категории
    task_name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)  # Описание задачи
    resource_link = models.URLField(blank=True, null=True)  # Ссылка на ресурс (статья/книга)
    task_number = models.IntegerField()  # Номер задания
    quote = models.TextField(null=True, blank=True)  # Цитата (необязательно)
    quote_author = models.CharField(max_length=255, null=True, blank=True)  # Автор цитаты (необязательно)

    def __str__(self):
        return f"{self.description} (Category: {self.category.name}, Level: {self.level})"


class CompletedTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.CharField(max_length=255)
    level = models.IntegerField()

    def __str__(self):
        return f"{self.task} (Level {self.level})"