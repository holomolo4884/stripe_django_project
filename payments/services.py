import stripe
from django.conf import settings
from decimal import Decimal


class StripeService:
    """
    Основной класс для работы со Stripe
    Поддерживает мультивалютность и разные типы платежей
    """
    def __init__(self, currency='usd'):
        self.currency = currency.lower()
        self._congihure_strip()

    def _congihure_strip(self):
        """
        Настройка Stripe с использованием секретного ключа для выбранной валюты
        """
        # Получаем ключи для данной валюты из настроек
        keys = settings.STRIPE_KEYS.get(self.currency)
        if not keys:
            raise ValueError(f"Нет ключей Stripe для валюты: {self.currency}")
