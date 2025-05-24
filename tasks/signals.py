from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task

previous_task_instances = {}

@receiver(post_save, sender=Task)
def capture_previous_instance(sender, instance, **kwargs):

    try:
        previous_task_instances[instance.pk] = Task.objects.get(pk=instance.pk)
    except Task.DoesNotExist:
        previous_task_instances[instance.pk] = None


@receiver(post_save, sender=Task)
def notify_status_change(sender, instance, created, **kwargs):

    if not created:
        try:

            db_instance_before_save = Task.objects.get(pk=instance.pk)

            if hasattr(instance, '_previous_status') and instance._previous_status != instance.status:
                print(f"--- Сповіщення (Сигнал Observer) ---")
                print(f"Статус завдання '{instance.title}' (ID: {instance.pk}) було змінено.")
                print(f"Попередній статус: {instance._previous_status}")
                print(f"Новий статус: {instance.status}")
                print(f"Проєкт: {instance.project.name}")

                print(f"------------------------------------")
            elif created:
                 print(f"--- Сповіщення (Сигнал Observer) ---")
                 print(f"Створено нове завдання '{instance.title}' (ID: {instance.pk}) зі статусом '{instance.status}'.")
                 print(f"Проєкт: {instance.project.name}")
                 print(f"------------------------------------")


        except Task.DoesNotExist:
            pass



from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Task
from django.core.mail import send_mail
from django.conf import settings

@receiver(pre_save, sender=Task)
def store_previous_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            previous_instance = Task.objects.get(pk=instance.pk)
            instance._previous_status = previous_instance.status
        except Task.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None

@receiver(post_save, sender=Task)
def notify_status_change(sender, instance, created, **kwargs):
    email_subject = ''
    email_message_body = ''
    recipient_list = ['makarenkovadym1302@gmail.com']

    if not created:
        if hasattr(instance, '_previous_status') and instance._previous_status is not None and instance._previous_status != instance.status:
            print(f"--- Сповіщення (Сигнал Observer) ---")
            print(f"Статус завдання '{instance.title}' (ID: {instance.pk}) було змінено.")
            print(f"Попередній статус: {instance._previous_status}")
            print(f"Новий статус: {instance.status}")
            print(f"Проєкт: {instance.project.name}")
            print(f"------------------------------------")

            email_subject = f'Зміна статусу завдання: "{instance.title}"'
            email_message_body = (
                f'Шановний користувач,\n\n'
                f'Статус завдання "{instance.title}" (ID: {instance.pk}) у проєкті "{instance.project.name}" було змінено.\n'
                f'Попередній статус: {instance._previous_status}\n'
                f'Новий статус: {instance.status}\n\n'
                f'Деталі завдання можна переглянути на сайті.\n'
                f'З повагою,\nВаша Система Управління Завданнями'
            )
    elif created:
        print(f"--- Сповіщення (Сигнал Observer) ---")
        print(f"Створено нове завдання '{instance.title}' (ID: {instance.pk}) зі статусом '{instance.status}'.")
        print(f"Проєкт: {instance.project.name}")
        print(f"------------------------------------")

        email_subject = f'Створено нове завдання: "{instance.title}"'
        email_message_body = (
            f'Шановний користувач,\n\n'
            f'У проєкті "{instance.project.name}" було створено нове завдання:\n'
            f'Назва: {instance.title}\n'
            f'Статус: {instance.status}\n'
            f'Опис: {instance.description or "Без опису"}\n\n'
            f'Деталі завдання можна переглянути на сайті.\n'
            f'З повагою,\nВаша Система Управління Завданнями'
        )

    # --- ДІАГНОСТИЧНІ PRINT ЗАЯВИ ---
    print(f"DEBUG: email_subject = '{email_subject}'")
    print(f"DEBUG: email_message_body = '{email_message_body[:50]}...' (перші 50 символів)") # Виводимо лише частину тіла листа
    print(f"DEBUG: recipient_list = {recipient_list}")
    print(f"DEBUG: settings.DEFAULT_FROM_EMAIL = {settings.DEFAULT_FROM_EMAIL}")
    # --- КІНЕЦЬ ДІАГНОСТИЧНИХ PRINT ЗАЯВ ---

    if email_subject and email_message_body:
        print("DEBUG: Умова для відправки листа виконана. Спроба відправки...")
        try:
            send_mail(
                email_subject,
                email_message_body,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
                fail_silently=False,
            )
            print(f"Email-сповіщення для завдання ID {instance.pk} мало б бути надіслано через SMTP.")
            print(f"Перевір поштову скриньку: {recipient_list}")
        except Exception as e:
            print(f"ПОМИЛКА SMTP при спробі надіслати email для завдання ID {instance.pk}: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("DEBUG: Умова для відправки листа НЕ виконана (email_subject або email_message_body порожні).")