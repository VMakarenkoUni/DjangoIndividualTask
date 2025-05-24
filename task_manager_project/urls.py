from django.contrib import admin
from django.urls import path, include # Переконайся, що 'include' тут є

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tasks.urls')), # Ось цей рядок підключає URL-и з твого додатку 'tasks'
                                     # Він каже: "всі URL-адреси, що починаються з кореня сайту (''),
                                     # шукай у файлі tasks.urls"
]