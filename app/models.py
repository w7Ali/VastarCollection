import sys
from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django_resized import ResizedImageField
from .utils import resize_image
from PIL import Image as PILImage

from .constants import CATEGORY_CHOICES, STATE_CHOICES, STATUS_CHOICES


class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    locality = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    zipcode = models.IntegerField()
    state = models.CharField(choices=STATE_CHOICES, max_length=50)

    def __str__(self):
        return self.user.username


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


# class Product(models.Model):
#     title = models.CharField(max_length=100)
#     selling_price = models.FloatField()
#     discounted_price = models.FloatField()
#     description = models.TextField()
#     brand = models.CharField(max_length=100)
#     category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
#     product_image = models.ImageField(upload_to="productimg", blank=True, null=True)

#     def save(self, *args, **kwargs):
#         if self.product_image:
#             img = PILImage.open(self.product_image)
#             if img.height > 700 or img.width > 400:
#                 output_size = (700, 400)
#                 img.thumbnail(output_size)
#                 in_mem_file = BytesIO()
#                 img.save(in_mem_file, format="JPEG", quality=95)
#                 in_mem_file.seek(0)
#                 self.product_image = InMemoryUploadedFile(
#                     in_mem_file,
#                     "ImageField",
#                     f"{self.product_image.name.split('.')[0]}.jpg",
#                     "image/jpeg",
#                     sys.getsizeof(in_mem_file),
#                     None,
#                 )
#         super(Product, self).save(*args, **kwargs)

#     def __str__(self):
#         return (
#             f"{self.title} | {self.brand} | {self.category} | {self.discounted_price}"
#         )


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

        # Below Property will be used by checkout.html page to show total cost in order summary

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

    # Below Property will be used by orders.html page to show total cost
    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price
