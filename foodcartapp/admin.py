from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import reverse, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from django.db import models

from .models import Restaurant, Product, RestaurantMenuItem, ProductCategory, Order, OrderItem
from django.templatetags.static import static

class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url)
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html('<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>', edit_url=edit_url, src=obj.image.url)
    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    pass


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ['product', 'quantity', 'cost']
    readonly_fields = ['cost']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'status', 'payment_method', '_total_cost', 'firstname',
        'lastname', 'address', 'phonenumber', 'comment'
    ]
    inlines = [OrderItemInline]
    ordering = ['id']

    def save_model(self, request, obj, form, change):
        for order_item in obj.items.all():    
            order_item.cost = order_item.get_order_item_cost()
            order_item.save()
        super().save_model(request, obj, form, change)

    def _total_cost(self, obj):
        return f"{obj.items.aggregate(models.Sum('cost'))['cost__sum']} руб."
    _total_cost.short_description = 'Сумма заказа'

    def response_change(self, request, obj):
        response = super().response_change(request, obj)
        if 'next' in request.GET:
            if url_has_allowed_host_and_scheme(request.GET['next'], settings.ALLOWED_HOSTS):
                return redirect(request.GET['next'])
        return response
