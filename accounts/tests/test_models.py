import pytest
from django.contrib.auth.models import User
from accounts.models import UserProfile, Level, Category, Task, CompletedTask

@pytest.mark.django_db
def test_user_profile_creation():
    user = User.objects.create_user(username='testuser', password='testpass123')
    profile = UserProfile.objects.create(user=user, birth_date='2000-01-01')

    assert profile.user.username == 'testuser'
    assert str(profile.birth_date) == '2000-01-01'
    assert profile.level == 1
    assert profile.completed_tasks == 0
    assert profile.current_task_number == 1
    assert profile.category == 'science'

@pytest.mark.django_db
def test_user_profile_update_current_task():
    user = User.objects.create_user(username='testuser', password='testpass123')
    profile = UserProfile.objects.create(user=user, completed_tasks=5)
    
    profile.update_current_task()

    assert profile.current_task_number == 6  # Должно увеличиться

@pytest.mark.django_db
def test_level_creation():
    level1 = Level.objects.create()
    level2 = Level.objects.create()

    assert level1.number == 1
    assert level1.level_type == 'mental'
    assert level2.number == 2
    assert level2.level_type == 'physical'

@pytest.mark.django_db
def test_category_creation():
    category = Category.objects.create(name='Наука')

    assert str(category) == 'Наука'

@pytest.mark.django_db
def test_task_creation():
    level = Level.objects.create()
    category = Category.objects.create(name='Спорт')
    task = Task.objects.create(
        level=level,
        category=category,
        task_name="Пробежка",
        description="Пробежка 5 км",
        task_number=1
    )

    assert task.task_name == "Пробежка"
    assert str(task) == "Пробежка 5 км (Category: Спорт, Level: 1)"

@pytest.mark.django_db
def test_completed_task_creation():
    user = User.objects.create_user(username='testuser', password='testpass123')
    completed_task = CompletedTask.objects.create(user=user, task="Пробежка", level=1)

    assert completed_task.task == "Пробежка"
    assert str(completed_task) == "Пробежка (Level 1)"
