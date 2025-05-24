from django.db import models
from django.contrib.auth.models import User # Якщо будеш використовувати систему користувачів Django

# Модель для Проєктів
class Project(models.Model):
    name = models.CharField(max_length=200, verbose_name="Назва проєкту")
    # owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects', null=True, blank=True, verbose_name="Власник")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Проєкт"
        verbose_name_plural = "Проєкти"

# Модель для Завдань
class Task(models.Model):
    STATUS_CHOICES = [
        ('New', 'Нове'),
        ('InProgress', 'В роботі'),
        ('Completed', 'Завершене'),
    ]

    title = models.CharField(max_length=255, verbose_name="Назва завдання")
    description = models.TextField(blank=True, null=True, verbose_name="Опис")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='New',
        verbose_name="Статус"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE, # Якщо видаляється проєкт, видаляються і всі його завдання
        related_name='tasks', # Дозволяє звертатися до завдань з об'єкту проєкту: project.tasks.all()
        verbose_name="Проєкт"
    )
    # assignee = models.ForeignKey(
    #     User,
    #     on_delete=models.SET_NULL, # Якщо користувач видаляється, завдання залишається без виконавця
    #     null=True,
    #     blank=True,
    #     related_name='assigned_tasks',
    #     verbose_name="Виконавець"
    # )
    parent_task = models.ForeignKey(
        'self', # Посилання на цю ж модель (Task)
        on_delete=models.CASCADE, # Якщо видаляється батьківське завдання, видаляються і дочірні
        null=True,
        blank=True,
        related_name='subtasks', # Дозволяє звертатися до підзавдань: task.subtasks.all()
        verbose_name="Батьківське завдання"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Завдання"
        verbose_name_plural = "Завдання"
        ordering = ['created_at'] # Сортування за замовчуванням