from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Главная страница
    path('', views.home, name='home'),
    # Эндпоинты
    path('buy/<int:item_id>/', views.buy_item, name='buy_item'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('api/create-order/', views.create_order, name='create_order'),
    path('api/create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
    # Страницы результатов
    path('success/', views.success_page, name='success'),
    path('cancel/', views.cancel_page, name='cancel'),
]