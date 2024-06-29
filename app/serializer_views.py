from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import CompanyDetail, Product
from .serializers import CompanyDetailSerializer, ProductSerializer


@api_view(["GET"])
def company_detail_api(request):
    try:
        # Get the active CompanyDetail
        company_detail = CompanyDetail.objects.get(is_active=True)
    except CompanyDetail.DoesNotExist:
        return Response(
            {"error": "Active company detail not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = CompanyDetailSerializer(company_detail)
    return Response(serializer.data, status=status.HTTP_200_OK)


from django.db.models import ExpressionWrapper, F, FloatField
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product
from .serializers import ProductSerializer


def calculate_discount_percentage(selling_price, discounted_price):
    """
    Helper function to calculate the discount percentage.
    """
    if selling_price != 0:
        return ((selling_price - discounted_price) / selling_price) * 100
    else:
        return 0


@api_view(["GET"])
def latest_and_discount_product(request):
    # Retrieve 4 latest products
    latest_products = Product.objects.order_by("-id")[:4]
    latest_serializer = ProductSerializer(latest_products, many=True)

    # Retrieve 2 products with highest percentage discount
    highest_discount_products = (
        Product.objects.annotate(
            discount_percentage=ExpressionWrapper(
                calculate_discount_percentage(
                    F("selling_price"), F("discounted_price")
                ),
                output_field=FloatField(),
            )
        )
        .exclude(discounted_price__isnull=True, discounted_price=0)
        .order_by("-discount_percentage")[:2]
    )

    highest_discount_serializer = ProductSerializer(
        highest_discount_products, many=True
    )

    # Combine both results into a single response
    data = {
        "latest_products": latest_serializer.data,
        "highest_discount_products": highest_discount_serializer.data,
    }
    return Response(data)
