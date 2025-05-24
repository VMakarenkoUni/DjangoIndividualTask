from django import forms
from .models import Project, Task

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name'] # Які поля з моделі Project показувати у формі
        labels = {
            'name': 'Назва проєкту'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введіть назву проєкту'})
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        # Поки що не включаємо 'project' та 'parent_task' сюди,
        # їх ми будемо обробляти у view, або передавати прихованими.
        # 'assignee' теж поки пропустимо для простоти.
        fields = ['title', 'description', 'status']
        labels = {
            'title': 'Назва завдання',
            'description': 'Опис',
            'status': 'Статус'
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введіть назву завдання'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Додайте опис'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }