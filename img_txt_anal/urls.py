from django.urls import path

from .views import home, add_doc, delete_doc_page, confirm_delete_doc, CustomLoginView, LogoutView, \
    analyse_doc_page, analyse_doc, input_id, cart_view, remove_from_cart, add_to_cart, process_payment, \
    register, get_text
from django.conf import settings
from django.conf.urls.static import static


"""URL приложения"""
urlpatterns = [
    path("", CustomLoginView.as_view(), name="login"),                                  # страница аутентификации и авторизации
    path("register/", register, name="register"),                                       # страница регистрации нового пользователя
    path("home", home, name="home"),                                                    # главная страница приложения
    path("add/", add_doc, name="add_doc"),                                              # страница добавления документа
    path("delete/", delete_doc_page, name="delete_doc_page"),                           # страница удаления документа
    path("confirm_delete/", confirm_delete_doc, name="confirm_delete_doc"),             # подтверждение удаления документа
    path("logout/", LogoutView.as_view(), name="logout"),                               # выход из приложения
    path("analyse/", analyse_doc_page, name="analyse_doc_page"),                        # страница заказа анализа документа
    path("complete_analyse/", analyse_doc, name="complete"),                            # подтверждение выполнения анализа документа
    path("input_id/", input_id, name="input_id"),                                       # страница на запрос вывода текста по ID
    path("get_text/", get_text, name="get_text"),                                       # страница с результатом анализа (вывод текста)
    path("add_to_cart/", add_to_cart, name="add_to_cart"),                              # добавление документа в корзину
    path("cart/", cart_view, name="cart_page"),                                         # страница корзины
    path("remove_from_cart/<int:item_id>/", remove_from_cart, name='remove_from_cart'), # удаление документа из корзины
    path("process_payment/", process_payment, name="process_payment"),                  # оплата товаров в корзине
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)