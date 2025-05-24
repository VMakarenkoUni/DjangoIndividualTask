from django.apps import AppConfig

class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'

    def ready(self):
        # Імпортуємо сигнали ТІЛЬКИ тут, всередині методу ready()
        import tasks.signals