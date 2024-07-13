from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import CompanyDetail, Product, Address
from .serializers import CompanyDetailSerializer, ProductSerializer, AddressSerializer
from django.db.models import ExpressionWrapper, F, FloatField


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
    # Retrieve 8 latest products
    latest_products = Product.objects.order_by("-id")[:8]
    latest_serializer = ProductSerializer(latest_products, many=True)

    # Retrieve 4 products with highest percentage discount
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
        .order_by("-discount_percentage")[:4]
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




@api_view(['PUT', 'PATCH'])
def update_address(request, id):
    try:
        address = Address.objects.get(pk=id)
    except Address.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = AddressSerializer(address, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_address(request, id):
    try:
        address = Address.objects.get(pk=id)
    except Address.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    address.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def set_active_address(request):
    user = request.user
    address_id = request.data.get('address_id')

    try:
        address = Address.objects.get(id=address_id, user=user)
    except Address.DoesNotExist:
        return Response({'success': False, 'error': 'Address not found'}, status=status.HTTP_404_NOT_FOUND)

    # Deactivate all addresses for this user
    Address.objects.filter(user=user).update(is_active=False)

    # Set the selected address as active
    address.is_active = True
    address.save()

    return Response({'success': True}, status=status.HTTP_200_OK)