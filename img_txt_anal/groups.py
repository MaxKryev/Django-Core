from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


def create_groups_and_permissions():
    """Создание группы Admin"""
    admin_group, created = Group.objects.get_or_create(name="Admin")
    if created:
        print("Admin group was created")
    else:
        print("Admin group already exist")

    permissions = Permission.objects.all()
    admin_group.permissions.set(permissions)

    """Создание группы Users"""
    user_group, created = Group.objects.get_or_create(name="Users")
    if created:
        print("Users group was created")
    else:
        print("Users group already exist")

    content_type = ContentType.objects.get(app_label="img_txt_anal", model="docs")
    view_permission = Permission.objects.get(codename='can_view', content_type=content_type)
    edit_permission = Permission.objects.get(codename='can_edit', content_type=content_type)
    user_group.permissions.set([view_permission, edit_permission])
