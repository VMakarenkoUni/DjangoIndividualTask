from django.shortcuts import render, redirect, get_object_or_404
from .models import Project, Task
from .forms import ProjectForm, TaskForm


# Головна сторінка або список проєктів
def project_list(request):
    projects = Project.objects.all().order_by('-created_at')
    return render(request, 'tasks/project_list.html', {'projects': projects})


# Сторінка створення нового проєкту
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('project_list')  # Перенаправлення на список проєктів
    else:
        form = ProjectForm()
    return render(request, 'tasks/project_form.html', {'form': form, 'title': 'Створити проєкт'})


# Сторінка одного проєкту (де будуть відображатися завдання)
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    # Отримуємо тільки кореневі завдання (ті, у яких parent_task is None)
    root_tasks = project.tasks.filter(parent_task__isnull=True).order_by('created_at')
    return render(request, 'tasks/project_detail.html', {'project': project, 'tasks': root_tasks}) # передаємо root_tasks як 'tasks'


# Сторінка створення завдання для конкретного проєкту
def create_task(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)  # Не зберігаємо одразу в базу
            task.project = project  # Встановлюємо зв'язок з проєктом
            # Тут пізніше можна буде інтегрувати Facade
            task.save()  # Тепер зберігаємо
            return redirect('project_detail', project_id=project.id)
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form, 'project': project, 'title': 'Створити завдання'})


# --- Початок реалізації Facade ---
# Для початку створимо простий сервісний клас, який потім буде частиною фасаду
class TaskService:
    def create_task_in_project(self, title, description, status, project_id, parent_task_id=None):
        project = get_object_or_404(Project, id=project_id)
        task_data = {
            'title': title,
            'description': description,
            'status': status,
            'project': project,
        }
        if parent_task_id:
            parent = get_object_or_404(Task, id=parent_task_id)
            task_data['parent_task'] = parent

        task = Task.objects.create(**task_data)
        # Тут може бути логіка сповіщень або інша бізнес-логіка
        return task


# Приклад Фасаду, як вимагалося [cite: 4, 10]
# Поки що він буде досить простим
class TaskManagerFacade:
    def __init__(self):
        self.task_service = TaskService()  # [cite: 12]

    def create_new_task(self, title, description, status, project_id, parent_task_id=None):  # Адаптуємо до полів форми
        # Тут може бути складніша логіка, координація кількох сервісів тощо.
        # Наприклад, валідація, створення пов'язаних об'єктів, логування.
        print(f"Facade: Спроба створити завдання '{title}' для проєкту ID {project_id}")
        task = self.task_service.create_task_in_project(title, description, status, project_id, parent_task_id)
        print(f"Facade: Завдання ID {task.id} створено успішно.")
        # Наприклад, тут можна було б викликати сервіс сповіщень, якби він був окремим
        return task


# --- Кінець реалізації Facade ---


# Оновлена view для створення завдання з використанням Facade
def create_task_with_facade(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            facade = TaskManagerFacade()
            try:
                facade.create_new_task(
                    title=form.cleaned_data['title'],
                    description=form.cleaned_data['description'],
                    status=form.cleaned_data['status'],
                    project_id=project.id
                    # parent_task_id можна буде додати пізніше, якщо буде поле у формі
                )
                return redirect('project_detail', project_id=project.id)
            except Exception as e:
                # Обробка можливих помилок з фасаду/сервісу
                form.add_error(None, f"Помилка створення завдання: {e}")
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html',
                  {'form': form, 'project': project, 'title': 'Створити завдання (Facade)'})