# serializers.py
from rest_framework import serializers

from .models import CompanyDetail, Product


class CompanyDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyDetail
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    discount_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = "__all__"

    def get_discount_percentage(self, obj):
        if obj.selling_price != 0:
            discount_percentage = (
                (obj.selling_price - obj.discounted_price) / obj.selling_price
            ) * 100
            return round(discount_percentage, 2)  # Round to 2 decimal places
        return 0
