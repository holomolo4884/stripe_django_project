import stripe
import json

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.conf import settings

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Item, Order, OrderItem, Discount, Tax

def home(request):
    """
    GET /
    Главная страница со списком всех товаров
    """
    items = Item.objects.all()
    return render(request, 'payments/home.html', {'items': items})

def item_detail(request, item_id):
    """
    GET /item/{id}/
    Страница товара с кнопкой Buy
    """
    item = get_object_or_404(Item, id=item_id)
    publishable_key = settings.STRIPE_KEYS[item.currency]['publishable']
    return render(
        request,
        'payments/item_detail.html',
        {'item': item, 'publishable_key': publishable_key}
    )

def success_page(request):
    """Страница успешной оплаты"""
    return render(request, 'payments/success.html')

def cancel_page(request):
    """Страница отмены оплаты"""
    return render(request, 'payments/cancel.html')

# API ЭНДПОИНТЫ

def buy_item(request, item_id):
    """
    GET /but/{id}
    Создает Stripe сессию и возвращает session.id
    """
    try:
        item = get_object_or_404(Item, id=item_id)
        stripe.api_key = settings.STRIPE_KEYS[item.currency]['secret']
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': item.currency,
                    'unit_amount': int(item.price * 100),
                    'product_data': {
                        'name': item.name,
                        'description': item.description,
                    },
                },
                'quantity': 1
            }],
            mode='payment',
            success_url='http://localhost:8000/success/',
            cancel_url='http://localhost:8000/cancel/',
        )

        return JsonResponse({'id': session.id})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(['POST'])
def create_order(request):
    """POST /api/create-order/"""
    try:
        data = json.loads(request.body)
        items_ids = data.get('items', [])

        if not items_ids:
            return JsonResponse({'error': 'Нет товаров'}, status=400)

        order = Order.objects.create()
        for item_id in items_ids:
            item = get_object_or_404(Item, id=item_id)
            OrderItem.objects.create(
                order=order,
                item=item,
                quantity=1,
                price_at_time=item.price,
            )

        if data.get('discount'):
            discount = get_object_or_404(Discount, id=data['discount'])
            order.discount = discount

        if data.get('tax'):
            tax = get_object_or_404(Tax, id=data['tax'])
            order.tax = tax

        order.calculate_total()
        order.save()

        first_item = order.items.first()
        stripe.api_key = settings.STRIPE_KEYS[first_item.currency]['secret']

        line_items = []
        for order_item in order.order_items.all():
            item = order_item.item
            line_items.append({
                'price_data': {
                    'currency': item.currency,
                    'unit_amount': int(item.price * 100),
                    'product_data': {
                        'name': item.name,
                    },
                },
                'quantity': order_item.quantity,
            })

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url='http://localhost:8000/success/',
            cancel_url='http://localhost:8000/cancel/',
        )

        order.stripe_session_id = session.id
        order.save()

        return JsonResponse({
            'session_id': session.id,
            'order_id': order.id,
            'total_amount': str(order.tota_amount),
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(['POST'])
def create_payment_intent(request):
    """POST /api/create-payment-intent/"""
    try:
        data = json.loads(request.body)
        order = get_object_or_404(Order, id=data['order_id'])

        first_item = order.items.first()
        stripe.api_key = settings.STRIPE_KEYS[first_item.currency]['secret']

        intent = stripe.PaymentIntent.create(
            amount=int(order.total_amount * 100),
            currency=first_item.currency,
            payment_method_types=['card'],
            metadata={'order_id': order.id},
        )

        order.stripe_payment_intent_id = intent.id
        order.save()

        return JsonResponse({
            'client_secret': intent.client_secret,
            'payment_intent_id': intent.id,
            'order_id': order.id,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)