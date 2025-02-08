from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('rankings/', rankings, name='rankings'),
    path('about/', about, name='about'),
    path('update_user/', update_user, name='update_user'),
    path('task/', task_view, name='task'),
    path('privacy_policy/',privacy_policy, name='privacy_policy'),
    path('delete_account/', delete_account, name='delete_account'),
    path('terms/', terms_and_conditions, name='terms'),
    path('user/<int:id>/', user_detail, name='user_detail'),
    path('profile/', profile, name='profile'),
]
