from django.urls import path
from . import views

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('project/new/', views.create_project, name='create_project'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    # Використовуємо нову view для створення завдання
    path('project/<int:project_id>/task/new/', views.create_task_with_facade, name='create_task_with_facade'),
    # Стару create_task можна закоментувати або видалити, якщо не потрібна
    # path('project/<int:project_id>/task/new_old/', views.create_task, name='create_task_old'),
]