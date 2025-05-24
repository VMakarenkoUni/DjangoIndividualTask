from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task
# from django.core.mail import send_mail # Для майбутньої відправки email
# from django.conf import settings # Для налаштувань email

# Ця змінна буде зберігати попередній стан завдання, щоб ми могли порівняти
# Це простий спосіб, для більш складних випадків можуть знадобитися інші підходи
previous_task_instances = {}

@receiver(post_save, sender=Task)
def capture_previous_instance(sender, instance, **kwargs):
    """
    Фіксує попередній стан завдання перед збереженням, якщо це оновлення.
    Це не зовсім "сигнальний" спосіб фіксації попереднього стану,
    краще було б використовувати pre_save, але для детекції зміни статусу
    в post_save нам потрібно знати, яким він був *до* збереження.

    Альтернативний і більш надійний спосіб - передавати 'update_fields'
    в save() і перевіряти, чи є 'status' серед них, або порівнювати
    з версією з БД до збереження, якщо можливо.

    Для нашої цілі, будемо порівнювати з тим, що було в БД до save().
    """
    try:
        previous_task_instances[instance.pk] = Task.objects.get(pk=instance.pk)
    except Task.DoesNotExist:
        # Це нове завдання, попереднього стану немає
        previous_task_instances[instance.pk] = None


@receiver(post_save, sender=Task)
def notify_status_change(sender, instance, created, **kwargs):
    """
    Цей сигнал спрацьовує ПІСЛЯ збереження об'єкту Task.
    """
    # Отримуємо попередній стан, якщо він був зафіксований
    # Цей підхід з глобальним dict не ідеальний для production, особливо з багатьма воркерами.
    # Для простоти зараз так.
    # previous_instance = previous_task_instances.get(instance.pk)

    # Більш простий спосіб перевірки зміни статусу, якщо ми не маємо pre_save стану:
    # Перевіряємо, чи це не новостворений об'єкт і чи змінився статус.
    # Щоб перевірити, чи змінився статус, нам потрібно знати його попереднє значення.
    # `update_fields` може допомогти, якщо `save()` викликається з ним.

    # Якщо це новостворене завдання, сповіщати про "зміну" статусу (з нічого на 'New') не будемо,
    # хіба що є така вимога. Фокусуємося на зміні існуючого.

    if not created: # Якщо завдання не було щойно створене, а оновлене
        try:
            # Отримуємо версію завдання з бази даних *до* поточного збереження.
            # Це не зовсім те, що було до редагування у формі, а те, що було в БД.
            # Якщо save() викликався кілька разів поспіль, це може бути не те, що очікується.
            # Для простоти, припустимо, що статус змінюється через адмінку або форму,
            # яка зберігає один раз.
            db_instance_before_save = Task.objects.get(pk=instance.pk) # Це вже буде instance *після* save в цьому сигналі
                                                                        # Тому цей підхід не спрацює тут напряму.

            # Ми можемо передати старий статус через саму інстанцію, якщо це можливо,
            # або використовувати `update_fields` при збереженні та перевіряти його.

            # Для простоти, зараз будемо реагувати на будь-яке збереження існуючого завдання
            # і просто виводити його поточний статус.
            # Щоб реально відстежити *зміну* статусу, потрібен pre_save сигнал або
            # порівняння з даними, які були до початку операції збереження.

            # Давайте спробуємо інший підхід: збережемо старий статус в атрибуті інстанції
            # за допомогою pre_save сигналу.

            if hasattr(instance, '_previous_status') and instance._previous_status != instance.status:
                print(f"--- Сповіщення (Сигнал Observer) ---")
                print(f"Статус завдання '{instance.title}' (ID: {instance.pk}) було змінено.")
                print(f"Попередній статус: {instance._previous_status}")
                print(f"Новий статус: {instance.status}")
                print(f"Проєкт: {instance.project.name}")
                # Тут можна додати логіку відправки email:
                # subject = f'Статус завдання "{instance.title}" змінено'
                # message = (
                #     f'Шановний користувач,\n\n'
                #     f'Статус завдання "{instance.title}" у проєкті "{instance.project.name}" було змінено.\n'
                #     f'Попередній статус: {instance._previous_status}\n'
                #     f'Новий статус: {instance.status}\n\n'
                #     f'Деталі завдання: http://127.0.0.1:8000/project/{instance.project.id}/ (посилання умовне)\n\n'
                #     f'З повагою,\nВаша Система Управління Завданнями'
                # )
                # try:
                #     send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, ['адреса_отримувача@example.com'])
                #     print("Email-сповіщення надіслано (симуляція).")
                # except Exception as e:
                #     print(f"Помилка відправки email: {e}")
                print(f"------------------------------------")
            elif created:
                 print(f"--- Сповіщення (Сигнал Observer) ---")
                 print(f"Створено нове завдання '{instance.title}' (ID: {instance.pk}) зі статусом '{instance.status}'.")
                 print(f"Проєкт: {instance.project.name}")
                 print(f"------------------------------------")


        except Task.DoesNotExist:
            # Це може статися, якщо завдання було видалено паралельно
            pass # нічого не робимо



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
    # Переконайся, що тут вказана реальна адреса, на яку ти хочеш отримувати тестові листи
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
            # Змінив повідомлення для SMTP
            print(f"Email-сповіщення для завдання ID {instance.pk} мало б бути надіслано через SMTP.")
            print(f"Перевір поштову скриньку: {recipient_list}")
        except Exception as e:
            print(f"ПОМИЛКА SMTP при спробі надіслати email для завдання ID {instance.pk}: {e}")
            import traceback
            traceback.print_exc() # Друкуємо повний traceback помилки
    else:
        print("DEBUG: Умова для відправки листа НЕ виконана (email_subject або email_message_body порожні).")