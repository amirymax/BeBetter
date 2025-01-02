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
]
