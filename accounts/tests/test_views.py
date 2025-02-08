import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import UserProfile

def test_home_view(client: Client):
    url = reverse('home')
    response = client.get(url)

    assert response.status_code == 200
    assert 'Добро пожаловать в BeBetter!' in response.content.decode()


def test_login_view(client: Client):
    url = reverse('login')
    response = client.get(url)

    assert response.status_code == 200
    assert 'Вход' in response.content.decode()


# test logout
@pytest.mark.django_db
def test_logout_view(client: Client):
    user = User.objects.create_user(username='testuser', password='testpass123')
    client.login(username='testuser', password='testpass123')

    url = reverse('logout')
    response = client.get(url)

    assert response.status_code == 302

    response = client.get(response.url)
    assert 'Добро пожаловать в BeBetter!' in response.content.decode()

def test_register_view(client: Client):
    url = reverse('register')
    response = client.get(url)

    assert response.status_code == 200
    assert 'Регистрация' in response.content.decode()


@pytest.mark.django_db
def test_rankings_view(client: Client):
    url = reverse('rankings')
    response = client.get(url)

    assert response.status_code == 200
    assert 'Рейтинг игроков' in response.content.decode()


def test_about_view(client: Client):
    url = reverse('about')
    response = client.get(url)

    assert response.status_code == 200
    assert 'О нас' in response.content.decode()


@pytest.mark.django_db
def test_home_view(client: Client):
    user = User.objects.create_user(username='testuser', password='testpass123')
    profile = UserProfile.objects.create(user=user, birth_date='1999-01-01')

    client.login(username='testuser', password='testpass123')

    url = reverse('home')
    response = client.get(url)

    assert response.status_code == 200
    assert 'Привет' in response.content.decode()


@pytest.mark.django_db
def test_task_view(client: Client):
    user = User.objects.create_user(username='testuser', password='testpass123')
    profile = UserProfile.objects.create(user=user, birth_date='1999-01-01')
    client.login(username='testuser', password='testpass123')

    url = reverse('task')  
    response = client.get(url)

    assert response.status_code == 200
    assert 'Уровень' in response.content.decode()


@pytest.mark.django_db
def test_profile_view(client: Client):
    user = User.objects.create_user(username='testuser', password='testpass123')
    profile = UserProfile.objects.create(user=user, birth_date='1999-01-01')
    client.login(username='testuser', password='testpass123')

    url = reverse('profile')
    response = client.get(url)

    assert response.status_code == 200
    assert 'testuser' in response.content.decode()


@pytest.mark.django_db
def test_update_user_view(client: Client):
    user = User.objects.create_user(username='testuser', password='testpass123')
    profile = UserProfile.objects.create(user=user, birth_date='1999-01-01')
    client.login(username='testuser', password='testpass123')

    # Check initial profile data
    url = reverse('profile')
    response = client.get(url)
    assert response.status_code == 200
    assert 'testuser' in response.content.decode()

    # Update user data
    url = reverse('update_user')
    data = {
        'first_name': 'New First Name',
        'username': 'newusername',
        'birth_date': '2000-01-01',
        'new_password': '',
        'confirm_password': ''
    }
    response = client.post(url, data)

    user.refresh_from_db()
    profile.refresh_from_db()

    # Check updated profile data
    url = reverse('profile')
    response = client.get(url)

    assert response.status_code == 200
    assert user.username == 'newusername'
    assert profile.birth_date.strftime('%Y-%m-%d') == '2000-01-01'


@pytest.mark.django_db
def test_delete_account_view(client: Client):
    user = User.objects.create_user(username='testuser', password='testpass123')
    client.login(username='testuser', password='testpass123')

    url = reverse('delete_account')
    response = client.post(url)

    assert response.status_code == 200
    assert 'Удаление аккаунта' in response.content.decode()

    # Enter correct password and delete account
    data = {'password': 'testpass123'}
    response = client.post(url, data)
    assert response.status_code == 302
    assert User.objects.filter(username='testuser').exists() is False


@pytest.mark.django_db
def test_user_detail_view(client: Client):
    user = User.objects.create_user(username='testuser', password='testpass123')
    profile = UserProfile.objects.create(user=user, birth_date='1999-01-01')
    client.login(username='testuser', password='testpass123')

    url = reverse('user_detail', args=[user.id])
    response = client.get(url)

    assert response.status_code == 200
    assert 'Профиль пользователя: testuser' in response.content.decode()


def test_privacy_policy_view(client: Client):
    url = reverse('privacy_policy')
    response = client.get(url)

    assert response.status_code == 200
    assert 'Политика конфиденциальности' in response.content.decode()


def test_terms_view(client: Client):
    url = reverse('terms')
    response = client.get(url)

    assert response.status_code == 200
    assert 'Условия использования' in response.content.decode()

