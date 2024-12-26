import os
import requests
import logging

from django.http import JsonResponse
from dotenv import load_dotenv
from django.contrib.auth.views import LoginView, LogoutView as AuthLogoutView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404

from .models import Docs, Cart, Price
from .forms import UserRegistrationForm
from .views_service import CartService, AddDocumentService, DeleteDocumentService, \
    AddToCartService, PaymentService, RegistrationUserService


"""Логирование"""

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


"""Ссылки на endpoints приложения Django REST"""

load_dotenv()

DJANGO_REST_API_URL = os.getenv("DJANGO_REST_API")
DJANGO_REST_API_URL_TOKEN = os.getenv("DJANGO_REST_API_TOKEN")
DJANGO_REST_API_URL_REGISTER = os.getenv("DJANGO_REST_API_REGISTER")


"Представление домашней страницы приложения"

@login_required
def home(request):
    docs = Docs.objects.all()

    has_items_in_cart, has_unpaid_items = CartService.get_cart_status(request.user)

    return render(request, "home.html", {
        "docs": docs,
        "user": request.user,
        "MEDIA_URL": settings.MEDIA_URL,
        "has_items_in_cart": has_items_in_cart,
        "has_unpaid_items": has_unpaid_items,
    })


"""Проверка JWT токенов"""

def check_jwt_tokens(request):
    access_token = request.COOKIES.get("access")
    logger.info(f"Access token from cookies: {access_token}")

    if access_token is None:
        refresh_token = request.COOKIES.get("refresh")
        if refresh_token is None:
            logger.warning("No access or refresh token found, redirecting to login.")
            return redirect("login")

        try:
            response = requests.post(f"{DJANGO_REST_API_URL_TOKEN}refresh/", data={'refresh': refresh_token})
            response.raise_for_status()
            new_tokens = response.json()
            access_token = new_tokens.get("access")
            refresh_token = new_tokens.get("refresh")
            logger.info(f"Access token refreshed successfully: {access_token}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to refresh token: {str(e)}")
            return redirect("login")

    headers = {"Authorization": f"Bearer {access_token}"}
    logger.info(f"Headers prepared for request: {headers}")
    return headers


"""Представление на добавление документа"""

@login_required
def add_doc(request):
    if request.method == "POST":
        file = request.FILES.get("file")
        file_path = default_storage.save(file.name, ContentFile(file.read()))
        full_file_path = os.path.join(settings.MEDIA_ROOT, file_path)
        size_kb = file.size / 1024
        logger.info(f"Doc_type: {file.content_type}, Doc_path: {file_path}, Doc_size: {size_kb}, Doc_full_path: {full_file_path}")
        headers = check_jwt_tokens(request)

        try:
            with open(full_file_path, 'rb') as f:
                upload_response = requests.post(
                    f"{DJANGO_REST_API_URL}/upload/",
                    files={'file': (file.name, f, file.content_type)},
                    headers=headers
                    )
            logger.info(f"Upload response: {upload_response.status_code}, {upload_response.text}")

            if upload_response.status_code == 200:
                external_id = upload_response.json().get("id", None)

                AddDocumentService.save_document(
                    file_path=file_path,
                    size_kb=size_kb,
                    external_id=external_id,
                    file_type=file.content_type,
                    user=request.user
                )

                return redirect("home")
            else:
                logger.error(f"Upload failed with status {upload_response.status_code}: {upload_response.text}")

        except Exception as e:
            logger.error(f"Error: {str(e)}")

        return redirect("add_doc")

    return render(request, "add_doc.html")


"""Представление на удаление документа"""

@login_required
def delete_doc_page(request):

    return render(request, 'delete_doc.html')


"""Представление на подтверждение удаления документа"""

@login_required
def confirm_delete_doc(request):
    if request.method == 'POST':
        doc_id = request.POST.get('doc_id')
        doc = get_object_or_404(Docs, id=doc_id)
        logger.info(doc_id,doc)
        headers = check_jwt_tokens(request)

        if request.user.has_perm('img_txt_anal.can_delete', doc):
            token = request.COOKIES.get("access")
            logger.info(token)

            data = {"doc_id": doc.external_id}
            logger.info(data)

            response = requests.delete(
                f"{DJANGO_REST_API_URL}/delete/{doc.external_id}",
                data=data,
                headers=headers,
            )
            logger.info(response)

            DeleteDocumentService.remove_file(doc.file_path)
            DeleteDocumentService.delete_document(doc)
            logger.info("Document deleted successfully")
        else:
            logger.info(request, "Delete error from FastAPI")
    else:
        logger.info(request, "You dont have rights to delete")

    return redirect("home")


"""Представление на страницу заказа анализа документа по ID"""

@login_required
def analyse_doc_page(request):
    return render(request, "analyse_doc_page.html")


"""Представление на выполнение анализа документа"""

@login_required
def analyse_doc(request):
    if request.method == 'POST':
        doc_id = request.POST.get("doc_id")
        doc = get_object_or_404(Docs, id=doc_id)
        logger.info(doc_id, doc)
        data = {"doc_id": doc.external_id}
        logger.info(data)
        headers = check_jwt_tokens(request)

        try:
            response = requests.post(
                f"{DJANGO_REST_API_URL}/analyse/{doc.external_id}",
                data=data,
                headers=headers,
            )
            logger.info(response)

            return render(request, "complete.html")
        except requests.exceptions.RequestException as e:
            complete_message = f"Analyse error: {str(e)}"

            return render(request,  "complete.html", {"complete_message": complete_message})

    return render(request, "complete.html")


"""Представление отображения на заказ получения текста по ID"""

@login_required
def input_id(request):

    return render(request, 'input_id.html')


"""Представление на отображение текста"""

@login_required
def get_text(request):
    if request.method == "POST":
        id_doc = request.POST.get('id')
        doc = get_object_or_404(Docs, id=id_doc)
        doc_id = doc.external_id
        logger.info(f"Document ID: {id_doc}, External ID: {doc_id}, Document: {doc}")
        headers = check_jwt_tokens(request)

        try:
            response = requests.get(
                f"{DJANGO_REST_API_URL}/get_text/{doc_id}",
                data={"doc_id": doc_id},
                headers=headers,
            )
            logger.info(f"Response: {response.json()}")

            return render(request, "get_text.html", {"text": response.json().get("text")})
        except Exception as e:
            logger.error(f"Ошибка при получении результатов анализа: {str(e)}")

            return JsonResponse({"error": str(e)}, status=500)


"""Представление на добавление документа в корзину"""

@login_required
def add_to_cart(request):
    if request.method == "POST":
        doc_id = request.POST.get("doc_id")

        if not doc_id:
            return redirect("home")

        doc = get_object_or_404(Docs, id=doc_id)
        price_obj = get_object_or_404(Price, file_type=doc.file_type)

        order_price = AddToCartService.calculate_order_price(doc, price_obj)
        AddToCartService.add_document_to_cart(request.user, doc, order_price)

    return render(request, "add_to_cart.html")


"""Представление на отображение корзины"""

@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user_id=request.user)
    total_price = cart_items.aggregate(total=Sum('order_price'))['total'] or 0

    return render(request, 'cart_page.html', {'cart_items': cart_items, 'total_price': total_price})


"""Представление для удаления документа из корзины"""

@login_required
def remove_from_cart(request, item_id):
    if request.method == "POST":
        item_to_remove = get_object_or_404(Cart, id=item_id)
        item_to_remove.delete()
        messages.success(request, 'Element is deleted from cart')

        return redirect('cart_page')


"""Оплата товаров в корзине"""

@login_required
def process_payment(request):
    if request.method == 'POST':
        if PaymentService.has_cart_items(request.user):
            cart_items = Cart.objects.filter(user=request.user, payment=False)
            PaymentService.mark_cart_items_as_paid(cart_items)

            return render(request, "process_payment.html")
        else:
            return redirect("cart_page")
    else:
        return redirect("cart_page")


"""Аутентификация и авторизация пользователя"""

class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    success_url = "home.html"

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")

        response = super().form_valid(form)

        data = {"username": username, "password": password}

        jwt_response = requests.post(f"{DJANGO_REST_API_URL_TOKEN}", json=data)

        if jwt_response.status_code == 200:
            tokens = jwt_response.json()
            access_token = tokens["access"]
            refresh_token = tokens["refresh"]

            response.set_cookie('access', access_token, max_age=300)
            response.set_cookie('refresh', refresh_token, max_age=3600)

        else:
            response = JsonResponse({"error": f"Failed to obtain JWT token from API. {jwt_response.status_code}"}, status=500)
        return response


"""Форма регистрации нового пользователя"""

def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            RegistrationUserService.create_user(form)

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            data = {'username': username, 'password': password}

            response = requests.post(f"{DJANGO_REST_API_URL_REGISTER}", json=data)

            if response.status_code == 201:
                return redirect("login")
            else:
                error_message = response.json().get('detail', 'Ошибка регистрации. Попробуйте позже.')
                form.add_error(None, error_message)
    else:
        form = UserRegistrationForm()

    return render(request, "registration/register.html", {"form": form})


"""Выход пользователя из системы"""

class LogoutView(AuthLogoutView):
    template_name = "registration/logout.html"