from django.test import TestCase, Client
from django.urls import reverse
from .models import Project, Task
from django.core import mail
from django.test import override_settings

class ProjectModelTest(TestCase):
    def test_project_creation(self):
        """Тестуємо створення об'єкта Project та його рядкове представлення."""
        project = Project.objects.create(name="My Test Project")
        self.assertEqual(project.name, "My Test Project")
        self.assertTrue(isinstance(project, Project))
        self.assertEqual(str(project), "My Test Project")

class TaskModelTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(name="Test Project for Tasks")

    def test_task_creation_default_status(self):
        """Тестуємо створення Task та статус за замовчуванням ('New')."""
        task = Task.objects.create(
            title="Test Task Default Status",
            project=self.project
        )
        self.assertEqual(task.title, "Test Task Default Status")
        self.assertEqual(task.status, "New")
        self.assertEqual(task.project, self.project)
        self.assertTrue(isinstance(task, Task))
        self.assertEqual(str(task), "Test Task Default Status")

    def test_task_creation_specific_status(self):
        """Тестуємо створення Task з конкретним статусом."""
        task = Task.objects.create(
            title="Test Task Specific Status",
            project=self.project,
            status="InProgress"
        )
        self.assertEqual(task.status, "InProgress")

    def test_task_with_parent(self):
        """Тестуємо створення підзавдання (ієрархія)."""
        parent_task = Task.objects.create(title="Parent Task", project=self.project)
        child_task = Task.objects.create(
            title="Child Task",
            project=self.project,
            parent_task=parent_task
        )
        self.assertEqual(child_task.parent_task, parent_task)
        self.assertIn(child_task, parent_task.subtasks.all())

    def test_task_status_choices(self):
        """Перевіряємо наявність очікуваних значень у STATUS_CHOICES."""
        valid_statuses = [choice[0] for choice in Task.STATUS_CHOICES]
        self.assertIn("New", valid_statuses)
        self.assertIn("InProgress", valid_statuses)
        self.assertIn("Completed", valid_statuses)

class ProjectViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.project1 = Project.objects.create(name="Project Alpha")
        self.project_list_url = reverse('project_list')
        self.create_project_url = reverse('create_project')
        self.project_detail_url = reverse('project_detail', args=[self.project1.id])

    def test_project_list_view_get(self):
        """Тестуємо доступність сторінки списку проєктів (GET)."""
        response = self.client.get(self.project_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/project_list.html')
        self.assertContains(response, self.project1.name)

    def test_create_project_view_post(self):
        """Тестуємо створення проєкту через POST-запит."""
        response = self.client.post(self.create_project_url, {'name': 'New Project via Test'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Project.objects.filter(name='New Project via Test').exists())

    def test_project_detail_view_get(self):
        """Тестуємо доступність сторінки деталей проєкту."""
        Task.objects.create(title="Task for Detail View", project=self.project1)
        response = self.client.get(self.project_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/project_detail.html')
        self.assertContains(response, self.project1.name)
        self.assertContains(response, "Task for Detail View")

class TaskViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.project = Project.objects.create(name="Project for Task Views")
        self.create_task_url = reverse('create_task_with_facade', args=[self.project.id])

    def test_create_task_view_post(self):
        """Тестуємо створення завдання для проєкту через POST-запит."""
        task_data = {
            'title': 'New Task from View Test',
            'description': 'Test description',
            'status': 'New'
        }
        response = self.client.post(self.create_task_url, task_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(title='New Task from View Test', project=self.project).exists())

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class TaskSignalWithLocMemTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(name="Project for Signal Test (LocMem)")

    def test_signal_on_task_create_locmem(self):
        """Тестуємо відправку email при створенні завдання (використовуючи locmem)."""
        Task.objects.create(title="Signal LocMem Create", project=self.project, status="New")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Створено нове завдання: "Signal LocMem Create"')

    def test_signal_on_task_status_change_locmem(self):
        """Тестуємо відправку email при зміні статусу завдання (використовуючи locmem)."""
        task = Task.objects.create(title="Signal LocMem Status Change", project=self.project, status="New")
        mail.outbox = []
        task.status = "Completed"
        task.save()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Зміна статусу завдання: "Signal LocMem Status Change"')
        self.assertIn("Новий статус: Completed", mail.outbox[0].body)