from django.contrib import admin
from django.urls import path, include # Переконайся, що 'include' тут є

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tasks.urls')),
]