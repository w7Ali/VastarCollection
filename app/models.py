import random
import sys
from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django_resized import ResizedImageField
from PIL import Image as PILImage

from .constants import CATEGORY_CHOICES, STATE_CHOICES, STATUS_CHOICES
from .utils import resize_image


class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    mobile_number = models.BigIntegerField(blank=True, null=True)
    user_image = models.ImageField(upload_to="userimg", blank=True, null=True)

    def __str__(self):
        return self.user.username


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    mobile_number = models.BigIntegerField(blank=True, null=True)
    locality = models.CharField(max_length=200)
    land_mark = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    zipcode = models.IntegerField()
    state = models.CharField(choices=STATE_CHOICES, max_length=50)
    is_active = models.BooleanField(default=False)


class CompanyDetail(models.Model):

    name = models.CharField(max_length=250, blank=True, null=True)
    subscription_email = models.EmailField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    office_address = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    pin_code = models.CharField(max_length=20, blank=True, null=True)
    area = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    office_number_1 = models.BigIntegerField(blank=True, null=True)
    office_number_2 = models.BigIntegerField(blank=True, null=True)
    gst_number = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.office_address


class Product(models.Model):
    title = models.CharField(max_length=100)
    selling_price = models.FloatField()
    discounted_price = models.FloatField()
    description = models.TextField()
    brand = models.CharField(max_length=100)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=20)
    product_image = models.ImageField(upload_to="productimg", blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.product_image:
            img = PILImage.open(self.product_image)
            if img.height > 700 or img.width > 400:
                output_size = (700, 400)
                img.thumbnail(output_size)
                in_mem_file = BytesIO()
                img.save(in_mem_file, format="JPEG", quality=95)
                in_mem_file.seek(0)
                self.product_image = InMemoryUploadedFile(
                    in_mem_file,
                    "ImageField",
                    f"{self.product_image.name.split('.')[0]}.jpg",
                    "image/jpeg",
                    sys.getsizeof(in_mem_file),
                    None,
                )
        super(Product, self).save(*args, **kwargs)

    @property
    def discount_percent(self):
        if self.selling_price != 0:
            return round(
                ((self.selling_price - self.discounted_price) / self.selling_price)
                * 100,
                2,
            )
        else:
            return 0

    def __str__(self):
        return (
            f"{self.title} | {self.brand} | {self.category} | {self.discounted_price}"
        )


class ProductVariation(models.Model):
    product = models.ForeignKey(
        Product, related_name="variations", on_delete=models.CASCADE
    )
    size = models.CharField(max_length=10)
    color = models.CharField(max_length=50)
    pieces_remaining = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.title} - {self.color} - {self.size}"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price


class OrderPlaced(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Pending")
    order_id = models.CharField(max_length=100, unique=False)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)  # Link to Address model

    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price

    def __str__(self):
        return f"Order {self.order_id} - {self.product.title}"



class Transaction(models.Model):
    order = models.OneToOneField(OrderPlaced, on_delete=models.CASCADE)
    shipping_address = models.JSONField()
    order_date = models.DateTimeField()
    total_cost = models.FloatField()
    order_items = models.JSONField()
    txn_id = models.CharField(max_length=255)
    payment_method_type = models.CharField(max_length=50)
    merchant_id = models.CharField(max_length=100)
    txn_uuid = models.CharField(max_length=255)
    gateway = models.CharField(max_length=50)
    card_details = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Transaction for Order {self.order.order_id}"
