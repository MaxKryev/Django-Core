from django.contrib import admin
from .models import Docs, UsersToDocs, Price, Cart


@admin.register(Docs)
class DocsAdmin(admin.ModelAdmin):
    list_display = ("file_path", "size")

@admin.register(UsersToDocs)
class UserToDocsAdmin(admin.ModelAdmin):
    pass

@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ("file_type", "price")

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "order_price", "payment")