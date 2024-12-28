from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import Task, UserProfile
from django.contrib.auth.models import User
from django.contrib import messages

def home(request):
    if request.user.is_authenticated:
        # Пользователь вошел в систему
        context = {
            "user": request.user,
        }
        return render(request, "home.html", context)
    else:
        # Пользователь не вошел
        return render(request, "welcome.html")


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Пароли не совпадают.')
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Имя пользователя уже занято.')
            return render(request, 'register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Электронная почта уже используется.')
            return render(request, 'register.html')

        # Создание пользователя
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)  # Вход сразу после регистрации
        messages.success(request, 'Вы успешно зарегистрировались!')
        return redirect('/')  # Редирект на главную страницу

    return render(request, 'register.html')  # Показать форму для GET-запроса

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def logout_view(request):
    # if request.method == 'POST':
    #     if request.POST.get('confirm') == 'yes':
    #         logout(request)
    #         return redirect('login')
    #     else:
    #         messages.error(request, 'Вы не подтвердили выход.')
    #         return redirect(request.META.get("HTTP_REFERER"))
    # return redirect(request.META.get("HTTP_REFERER"))
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы!')
    return redirect('home')


def user_dashboard(request):
    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)

        # Текущая задача
        current_task = Task.objects.filter(user=request.user, is_completed=False).order_by("level").first()

        # Предыдущие задачи
        previous_tasks = Task.objects.filter(user=request.user, is_completed=True).order_by("-level")

        context = {
            "user": request.user,
            "profile": profile,
            "current_task": current_task,
            "previous_tasks": previous_tasks,
        }
        return render(request, "dashboard.html", context)
    else:
        return redirect("login")