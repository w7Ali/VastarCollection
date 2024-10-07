from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    Address,
    Cart,
    CompanyDetail,
    Customer,
    OrderPlaced,
    Product,
    ProductVariation,
    Receipt,
    Transaction,
)

# from unfold.admin import ModelAdmin


@admin.register(Customer)
class CustomerModelAdmin(ModelAdmin):
    list_display = ["id", "user", "first_name", "last_name", "city", "mobile_number"]
    search_fields = ["first_name", "last_name", "city", "mobile_number"]
    list_filter = ["city"]


@admin.register(Address)
class AddressModelAdmin(ModelAdmin):
    list_display = [
        "id",
        "user",
        "full_name",
        "mobile_number",
        "locality",
        "land_mark",
        "city",
        "zipcode",
        "state",
        "is_active",
    ]
    search_fields = ["full_name", "city", "zipcode"]
    list_filter = ["state", "city", "is_active"]


@admin.register(Receipt)
class ReceiptModelAdmin(ModelAdmin):
    list_display = [field.name for field in Receipt._meta.fields]


@admin.register(Product)
class ProductModelAdmin(ModelAdmin):
    list_display = [
        "id",
        "title",
        "selling_price",
        "discounted_price",
        "description",
        "brand",
        "category",
        "product_image",
    ]


@admin.register(Cart)
class CartModelAdmin(ModelAdmin):
    list_display = ["id", "user", "product", "quantity"]


@admin.register(OrderPlaced)
class OrderPlacedModelAdmin(ModelAdmin):
    list_display = [
        "id",
        "user",
        "customer",
        "customer_info",
        "product",
        "product_info",
        "quantity",
        "ordered_date",
        "status",
    ]

    def product_info(self, obj):
        link = reverse("admin:app_product_change", args=[obj.product.pk])
        return format_html('<a href="{}">{}</a>', link, obj.product.title)

    def customer_info(self, obj):
        link = reverse("admin:app_customer_change", args=[obj.customer.pk])
        return format_html('<a href="{}">{}</a>', link, obj.customer)


@admin.register(CompanyDetail)
class CompanyDetailAdmin(ModelAdmin):
    list_display = (
        "name",
        "office_address",
        "subscription_email",
        "contact_email",
        "gst_number",
        "is_active",
    )
    list_filter = ("state", "city", "country", "is_active")
    search_fields = (
        "office_address",
        "subscription_email",
        "contact_email",
        "gst_number",
    )

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "office_address",
                    "subscription_email",
                    "contact_email",
                    "gst_number",
                )
            },
        ),
        (
            "Location Information",
            {"fields": ("state", "city", "pin_code", "area", "country")},
        ),
        ("Contact Numbers", {"fields": ("office_number_1", "office_number_2")}),
        ("Active", {"fields": ("is_active",)}),
    )


@admin.register(ProductVariation)
class ProductVariationAdmin(ModelAdmin):
    list_display = ["id", "product", "size", "color", "pieces_remaining"]

@admin.register(Transaction)
class TransactionVariationAdmin(ModelAdmin):
    list_display = ["id", "order", "shipping_address", "order_date", "total_cost", "order_items"]
