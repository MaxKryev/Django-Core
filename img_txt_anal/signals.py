from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def add_user_to_group(sender, instance, created, **kwargs):
    """Добавляем пользователя в группу Users при регистрации"""
    if created:
        user_group, _ = Group.objects.get_or_create(name="Users")
        instance.groups.add(user_group)
