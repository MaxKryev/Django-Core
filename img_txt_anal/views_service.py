import os
import requests

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .models import Cart, Docs, UsersToDocs


"""Логика представления домашней страницы"""

class CartService:
    @staticmethod
    def get_cart_status(user):
        has_items_in_cart = Cart.objects.filter(user=user).exists()
        has_unpaid_items = Cart.objects.filter(user=user, payment=False).exists()
        return has_items_in_cart, has_unpaid_items


"""Логика представления добавления документа"""

class AddDocumentService:

    def upload_to_fastapi(self, file, fastapi_upload_url):
        self.file_content = file.read()
        self.file_type = file.content_type

        response = requests.post(fastapi_upload_url, files={"file": (file.name, self.file_content, self.file_type)})
        if response.status_code == 200:
            return response.json().get("id"), file.size / 1024 , self.file_type
        return None, None, None

    @staticmethod
    def save_document(file_path, external_id, size_kb, file_type, user):
        doc_instance = Docs.objects.create(
            file_path=file_path,
            size=size_kb,
            external_id=external_id,
            file_type=file_type
        )
        UsersToDocs.objects.create(username=user, docs_id=doc_instance)


"""Логика представления подтверждения удаления документа"""

class DeleteDocumentService:
    @staticmethod
    def delete_from_fastapi(external_id, fastapi_delete_url):
        response = requests.delete(f"{fastapi_delete_url}/{external_id}")
        return response.status_code == 200

    @staticmethod
    def remove_file(file_path):
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        if os.path.exists(full_path):
            os.remove(full_path)

    @staticmethod
    def delete_document(doc):
        doc.delete()


"""Логика представления анализа документа"""

class AnalyseDocumentService:
    @staticmethod
    def analyse(external_id, fastapi_analyse_url):
        response = requests.post(f"{fastapi_analyse_url}/{external_id}")
        response.raise_for_status()
        return response.status_code


"""Логика представления просмотра текста"""

class GetTextDocumentService:
    @staticmethod
    def fetch_text(external_id, fastapi_get_text_url):
        response = requests.get(f"{fastapi_get_text_url}/{external_id}")
        response.raise_for_status()
        return response.json().get("text")


"""Логика представления добавления документа в корзину"""

class AddToCartService:
    @staticmethod
    def calculate_order_price(doc, price_obj):
        price_value = price_obj.price

        if isinstance(doc.size, (int, float)):
            size_value = doc.size
        else:
            size_value = float(doc.size)

        return price_value * size_value

    @staticmethod
    def add_document_to_cart(user, doc, order_price):
        try:
            cart_item = Cart.objects.create(user=user, docs=doc, order_price=order_price)
            return cart_item
        except ValidationError as e:
            raise
        except Exception as e:
            raise


"""Логика представления оплаты товаров в корзине"""

class PaymentService:
    @staticmethod
    def mark_cart_items_as_paid(cart_items):
        for item in cart_items:
            item.payment = True
            item.save()

    @staticmethod
    def has_cart_items(user):
        return Cart.objects.filter(user=user, payment=False).exists()


"""Логика регистрации нового пользователя"""

User = get_user_model()

class RegistrationUserService:
    @staticmethod
    def create_user(form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data["password"])
        user.save()
        return user