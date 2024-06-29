from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    Cart,
    CompanyDetail,
    Customer,
    OrderPlaced,
    Product,
    ProductVariation,
)


@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "name", "locality", "city", "zipcode", "state"]


@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
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
class CartModelAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "product", "quantity"]


@admin.register(OrderPlaced)
class OrderPlacedModelAdmin(admin.ModelAdmin):
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
        return format_html('<a href="{}">{}</a>', link, obj.customer.name)


@admin.register(CompanyDetail)
class CompanyDetailAdmin(admin.ModelAdmin):
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
class ProductVariationAdmin(admin.ModelAdmin):
    list_display = ["id", "product", "size", "color", "pieces_remaining"]
