import hashlib
import uuid
import logging
import requests
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.conf import settings
from .models import Cart, Customer, OrderPlaced, Address
from .views import process_cart_items
logger = logging.getLogger(__name__)

@login_required
def initiate_payment_payu(request):
    user = request.user
    logger.info(f"User: {user.username} initiating payment.")

    cart_items = Cart.objects.filter(user=user)
    if not cart_items.exists():
        logger.warning("No cart items found.")
        return JsonResponse({"message": "No cart items found"}, status=404)

    customer = Customer.objects.filter(user=user).first()
    if not customer:
        messages.info(request, "Please fill out your profile details to continue with the payment.")
        return redirect("profile")

    amount = sum(p.quantity * p.product.discounted_price for p in cart_items)
    shipping_amount = 70.0
    totalamount = amount + shipping_amount
    order_id = f"order-{uuid.uuid4()}"
    selected_address_id = request.POST.get('custid')

    logger.info(f"Total amount: {totalamount}, Order ID: {order_id}")

    try:
        selected_address = Address.objects.get(id=selected_address_id)
        logger.info(f"Selected address: {selected_address}")
    except Address.DoesNotExist:
        messages.error(request, "Selected address does not exist.")
        return redirect("checkout")

    # Create OrderPlaced records
    for cart_item in cart_items:
        OrderPlaced.objects.create(
            user=user,
            customer=customer,
            product=cart_item.product,
            quantity=cart_item.quantity,
            status="Pending",
            order_id=order_id,
            address=selected_address
        )
        logger.info(f"Order placed for product: {cart_item.product.title}, Quantity: {cart_item.quantity}")


    hash_value = generate_hash(key=settings.PAYU_MERCHANT_KEY,txnid=order_id, amount=totalamount, productinfo="Cart Items", firstname=customer.first_name, email=user.email, salt=settings.PAYU_MERCHANT_SALT)
    print("\n\n\nGenerated Hash Value:::", hash_value)
    payload = {
        "key": settings.PAYU_MERCHANT_KEY,
        "txnid": order_id,
        "amount": str(totalamount),
        "productinfo": "Cart Items",
        "firstname": customer.first_name,
        "email": user.email,
        "phone": str(customer.mobile_number),
        "surl": request.build_absolute_uri(settings.PAYU_SUCCESS_URL),
        "furl": request.build_absolute_uri(settings.PAYU_FAILURE_URL),
        "hash": hash_value,
        "address1": selected_address.locality,
        "address2": selected_address.land_mark,
        "city": selected_address.city,
        "state": selected_address.state,
        "zipcode": selected_address.zipcode,
    }
    logger.info(f"Payload for PayU: {payload}")

    try:
        response = processed_payu(payload)
        logger.info(f"Response from PayU: {response.status_code}, Content: {response.content}")
        if response.status_code == 200:
            return redirect(response.url)
        else:
            messages.error(request, "Payment processing failed. Please try again.")
            return redirect("checkout")
    except Exception as e:
        logger.error(f"An error occurred while processing payment for user {user.id}: {str(e)}")
        messages.error(request, "An error occurred while processing your payment.")
        return redirect("checkout")

def generate_payu_hash(txnid, amount, firstname, email):
    # Generate the hash using the parameters
    hash_string = f"{settings.PAYU_MERCHANT_KEY}|{txnid}|{amount}|Cart Items|{firstname}|{email}||||||||||{settings.PAYU_MERCHANT_SALT}"
    logger.debug(f"Hash data: {hash_string}")  # Log the data for debugging
    return hashlib.sha512(hash_string.encode('utf-8')).hexdigest()


def generate_hash(key, txnid, amount, productinfo, firstname, email, salt):
    input_str = f"{key}|{txnid}|{amount}|{productinfo}|{firstname}|{email}|||||||||||{salt}"
    return hashlib.sha512(input_str.encode('utf-8')).hexdigest()


@csrf_exempt
def payment_done_payu(request):
    response_data = request.POST.dict()
    order_id = response_data.get("txnid")
    status = response_data.get("status")
    logger.info(f"Payment response: Order ID: {order_id}, Status: {status}")

    if status == "success":
        orders = OrderPlaced.objects.filter(order_id=order_id)
        if orders.exists():
            for order in orders:
                order.status = "Accepted"
                order.save()
                logger.info(f"Order {order_id} status updated to Accepted.")
                return process_cart_items(order.user, order_id)

    return render(request, "app/payment_failed.html", {"order_id": order_id})
    
def processed_payu(params):
    url = "https://test.payu.in/_payment"
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded"
    }
    
    logger.info("Sending payload to PayU...")
    response = requests.post(url, data=params, headers=headers)
    return response
