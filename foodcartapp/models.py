from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone


class Restaurant(models.Model):
    name = models.CharField('название', max_length=50)
    address = models.CharField('адрес', max_length=100, blank=True)
    contact_phone = models.CharField('контактный телефон', max_length=50, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'


class ProductQuerySet(models.QuerySet):
    def available(self):
        return self.distinct().filter(menu_items__availability=True)


class ProductCategory(models.Model):
    name = models.CharField('название', max_length=50)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField('название', max_length=50)
    category = models.ForeignKey(ProductCategory, null=True, blank=True, on_delete=models.SET_NULL,
                                 verbose_name='категория', related_name='products')
    price = models.DecimalField(
        'цена', max_digits=8, decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField('картинка')
    special_status = models.BooleanField('спец.предложение', default=False, db_index=True)
    ingridients = models.CharField('ингредиенты', max_length=200, blank=True)

    objects = ProductQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='menu_items')
    availability = models.BooleanField('в продаже', default=True, db_index=True)

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]


class OrderQuerySet(models.QuerySet):  
    def get_total_cost(self):
        return self.annotate(total_cost=models.Sum('items__cost'))


class Order(models.Model):
    firstname = models.CharField('Имя', max_length=50, db_index=True)
    lastname = models.CharField('Фамилия', max_length=50, db_index=True)
    phonenumber = PhoneNumberField(
        'Номер телефона', db_index=True,
        help_text='8 800 555 35 35'
    )
    address = models.TextField(
        'Адрес', help_text='ул.Пушкина, д. Колотушкина', db_index=True
    )
    STATUS_CHOICES = [('Done', 'Выполнен'), ('In progress', 'В работе')]
    status = models.CharField(
        'Статус', max_length=11, default='In progress',
        choices=STATUS_CHOICES, db_index=True
    )
    PAYMENT_CHOICES = [('Cash', 'Наличными'), ('By card', 'Картой')]
    payment_method = models.CharField(
        'Способ оплаты', max_length=11, default='Cash',
        choices=PAYMENT_CHOICES, db_index=True
    )
    comment = models.TextField(
        'Комментарий', help_text='Плюнуть в бургер', blank=True,
        db_index=True
    )
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    called_at = models.DateTimeField(null=True, blank=True, db_index=True)
    delivered_at = models.DateTimeField(null=True, blank=True, db_index=True)

    def __str__(self):
        return f'Заказ {self.id}'

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, verbose_name='Заказ',
        related_name='items',
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        verbose_name='Продукт',
        related_name='order_items',
    )
    quantity = models.IntegerField(
        'Количество',
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    cost = models.DecimalField(
        'Стоимость', max_digits=8, decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    def get_order_item_cost(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f'{self.product.name} в заказе {self.order.id}'

    class Meta:
        verbose_name = 'позиция'
        verbose_name_plural = 'позиции'
