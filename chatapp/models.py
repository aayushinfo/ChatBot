from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class CustomUser(AbstractUser):
    name = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(blank=False, max_length=254, verbose_name='email address', unique=True)
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    user_status = models.IntegerField(null=True, blank=True, default=0)
    updated_at = models.IntegerField(null=True, blank=True, default=None)
    deleted_at = models.IntegerField(null=True, blank=True, default=None)

    groups = models.ManyToManyField(Group, related_name='custom_user_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions')

    def __str__(self):
        return self.name

class Messages(models.Model):
    message = models.CharField(max_length=1000, null=False, blank=False)
    sender_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False, blank=False, related_name='sent_messages')
    receiver_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False, blank=False, related_name='received_messages')
    replies_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.message

