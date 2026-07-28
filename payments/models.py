from django.db import models
from django.core.validators import MinValueValidator


class Item(models.Model):
    """
    Модель товара
    Хранит информацию о продукте: название, описание, цену и валюту
    """
    CURRENCY_CHOICES = [
        ('rub', 'RUB - Российский рубль'),
        ('usd', 'USD - Доллар США'),
    ]

    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name="Цена"
    )
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='usd',
                                verbose_name="Валюта")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

    def __str__(self):
        return f"{self.name} ({self.currency.upper()} {self.price})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


class Discount(models.Model):
    """
    Модель скидки
    Может быть в процентах или фиксированной сумме
    """
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Процентная'),
        ('fixed', 'Фиксированная'),
    ]

    name = models.CharField(max_length=255, verbose_name="Название")
    type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES,
        default='percentage',
        verbose_name="Тип"
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Значение"
    )
    stripe_coupon_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID купона в Stripe"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")

    def __str__(self):
        return f"{self.name} ({self.value}{'%' if self.type == 'percentage' else ' USD'})"

    def get_stripe_discount_data(self, currency='usd'):
        """
        Получение данных для Stripe в правильном формате
        Если у скидки есть ID купона в Stripe - используем его
        Иначе создаем новый купон на основе данных
        """
        if self.stripe_coupon_id:
            return {'coupon': self.stripe_coupon_id}

        if self.type == 'percentage':
            # Для процентной скидки
            return {
                'percentage_off': float(self.value)
            }
        else:
            # Для фиксированной скидки (переводим в центы)
            return {
                'amount_off': int(self.value * 100),
                'currency': currency
            }

    class Meta:
        verbose_name = "Скидка"
        verbose_name_plural = "Скидки"


class Tax(models.Model):
    """
    Модель налога
    Может быть в процентах или фиксированной сумме
    """
    TAX_TYPE_CHOICES = [
        ('percentage', 'Процентный'),
        ('fixed', 'Фиксированный'),
    ]

    name = models.CharField(max_length=255, verbose_name="Название")
    type = models.CharField(
        max_length=20,
        choices=TAX_TYPE_CHOICES,
        default='percentage',
        verbose_name="Тип"
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Значение"
    )
    stripe_tax_rate_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID налоговой ставки в Stripe"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    def __str__(self):
        return f"{self.name} ({self.value}{'%' if self.type == 'percentage' else ' USD'})"

    def get_stripe_tax_data(self):
        """
        Получение данных для Stripe
        Stripe поддерживает только процентные налоги,
        поэтому для фиксированных мы создаем специальный налог
        """
        if self.stripe_tax_rate_id:
            return {'tax_rate': self.stripe_tax_rate_id}

        if self.type == 'percentage':
            return {
                'percentage': float(self.value),
                'inclusive': False  # Налог добавляется сверху
            }
        else:
            # Для фиксированного налога используем процент 0%
            # и добавляем описание для отображения
            return {
                'percentage': 0,
                'inclusive': False,
                'description': f"Фиксированный налог: {self.value}"
            }

    class Meta:
        verbose_name = "Налог"
        verbose_name_plural = "Налоги"


class Order(models.Model):
    """
    Модель заказа
    Объединяет несколько товаров в один заказ с общими скидками и налогами
    """
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('failed', 'Ошибка оплаты'),
        ('refunded', 'Возвращен'),
    ]

    items = models.ManyToManyField(Item, through='OrderItem', verbose_name="Товары")
    discount = models.ForeignKey(
        Discount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Скидка"
    )
    tax = models.ForeignKey(
        Tax,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Налог"
    )
    stripe_session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID сессии Stripe"
    )
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID платежного намерения Stripe"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Общая сумма"
    )
    currency = models.CharField(max_length=3, default='usd', verbose_name="Валюта")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

    def __str__(self):
        return f"Заказ #{self.id} - {self.status} ({self.currency.upper()} {self.total_amount})"

    def calculate_total(self):
        """Рассчет общей суммы заказа с учетом скидок и налогов"""
        subtotal = sum(item.price for item in self.items.all())

        discount_amount = 0
        if self.discount:
            if self.discount.type == 'percentage':
                discount_amount = (self.discount.value / 100) * subtotal
            else:
                discount_amount = self.discount.value

        total = subtotal - discount_amount

        if self.tax:
            if self.tax.type == 'percentage':
                total = total * (1 + self.tax.value / 100)
            else:
                total = total + self.tax.value

        self.total_amount = total
        self.save()
        return total

    def get_currency(self):
        """Определяем валюту заказа по первому товару"""
        first_item = self.items.first()
        return first_item.currency if first_item else 'usd'

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class OrderItem(models.Model):
    """
    Промежуточная модель для связи Order и Item
    Позволяет хранить количество товара и цену на момент заказа
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name="Заказ"
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        verbose_name="Товар"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    price_at_time = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена на момент заказа"
    )

    def __str__(self):
        return f"{self.item.name} x {self.quantity} в заказе #{self.order.id}"

    def save(self, *args, **kwargs):
        """При сохранении запоминаем текущую цену товара"""
        if not self.price_at_time:
            self.price_at_time = self.item.price
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"