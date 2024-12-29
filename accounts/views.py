from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import  UserProfile, Task, CompletedTask
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

def home(request):
    if request.user.is_authenticated:
        # Пользователь вошел в систему
        user_profile = UserProfile.objects.get(user=request.user)
    
        # Получаем текущую задачу
        current_task = Task.objects.filter(level=user_profile.level).first()
        resource_link = current_task.resource_link if current_task and current_task.resource_link else None
        # Получаем список предыдущих выполненных задач
        previous_tasks = CompletedTask.objects.filter(user=request.user).order_by('-level')

        context = {
            'user_profile': user_profile,
            'current_task': current_task,
            'previous_tasks': previous_tasks,
            'resource_link': resource_link
        }
        return render(request, "home.html", context)
    else:
        # Пользователь не вошел
        return render(request, "welcome.html")


def register(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        username = request.POST.get("username")
        birth_date = request.POST.get("birth_date")
        category = request.POST.get("category")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Пароли не совпадают.")
            return render(request, "register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Имя пользователя уже занято.")
            return render(request, "register.html")

        # Создаем пользователя
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            password=password,
        )
        # Создаем профиль пользователя
        UserProfile.objects.create(
            user=user,
            category=category,
        )
        login(request, user)
        return redirect("/")
    return render(request, "register.html")

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
    # messages.success(request, 'Вы успешно вышли из системы!')
    return redirect('home')

def about(request):
    return render(request, "about.html")

def rankings(request):
    # Получаем фильтр категории из GET-параметров
    category_filter = request.GET.get('category')

    # Если категория указана, фильтруем по ней
    if category_filter:
        players = UserProfile.objects.filter(category=category_filter).order_by('-level', '-completed_tasks')
    else:
        players = UserProfile.objects.all().order_by('-level', '-completed_tasks')

    # Пагинация
    paginator = Paginator(players, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Если пользователь вошел в систему, определяем его место
    user_rank = None
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)
        user_rank = list(players).index(user_profile) + 1

    context = {
        'page_obj': page_obj,
        'user_rank': user_rank,
        'category_filter': category_filter,  # Передаем выбранный фильтр в шаблон
    }
    return render(request, 'rankings.html', context)

@login_required
def update_user(request):
    # Проверяем, существует ли профиль для текущего пользователя
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        username = request.POST.get("username")
        birth_date = request.POST.get("birth_date")
        category = request.POST.get("category")
        
        # Проверка на уникальность имени пользователя
        if User.objects.filter(username=username).exclude(id=request.user.id).exists():
            messages.error(request, "Имя пользователя уже занято.")
        else:
            # Обновление данных пользователя
            request.user.first_name = first_name
            request.user.username = username
            request.user.save()

            # Обновление данных профиля
            user_profile.birth_date = birth_date
            user_profile.category = category
            user_profile.save()

            messages.success(request, "Профиль успешно обновлен.")
            return redirect("update_user")

    context = {
        "user_profile": user_profile,
    }
    return render(request, "update_user.html", context)