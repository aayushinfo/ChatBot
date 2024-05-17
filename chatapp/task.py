from celery import shared_task
from chatapp.models import Messages, CustomUser

@shared_task
def send_scheduled_message(message_id):
    try:
        message = Messages.objects.get(id=message_id)
        # Logic to send the message
        # For example, you could save it to a 'sent' state or perform another action
        message.sent = True
        message.save()
    except Messages.DoesNotExist:
        # Handle the case where the message does not exist
        pass
