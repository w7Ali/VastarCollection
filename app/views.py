import base64
import hashlib
import hmac
import json
import logging
import random
import urllib.parse
import uuid
from datetime import datetime
import ast
from django.views.decorators.http import require_GET

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from io import BytesIO
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import get_template
from django.core.files.base import ContentFile

from reportlab.pdfgen import canvas


from .forms import AddressForm, CustomerProfileForm, CustomerRegistrationForm, LoginForm
from .models import Address, Cart, Customer, OrderPlaced, Product, ProductVariation, Transaction

logger = logging.getLogger("app")


class CustomLoginView(LoginView):
    template_name = "app/authentication/login.html"
    authentication_form = LoginForm
    success_url = reverse_lazy("profile")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse_lazy("profile"))
        return super().dispatch(request, *args, **kwargs)


@method_decorator(csrf_exempt, name="dispatch")
class ProductView(View):
    def get(self, request):
        totalitem = 0

        mens_wear = list(Product.objects.filter(category="MW"))
        womens_wear = list(Product.objects.filter(category="WW"))

        combined_products = mens_wear + womens_wear
        random.shuffle(combined_products)

        paginator = Paginator(combined_products, 12)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        if request.user.is_authenticated:
            totalitem = Cart.objects.filter(user=request.user).count()

        return render(
            request,
            "app/index.html",
            {
                "page_obj": page_obj,
                "totalitem": totalitem,
            },
        )


class ProductDetailView(View):
    """
    View to display details of a single product.
    """

    def get(self, request, pk):
        totalitem = 0
        product = get_object_or_404(Product, pk=pk)
        product_variation = ProductVariation.objects.filter(product=product)
        availability = product_variation.exists()

        item_already_in_cart = False
        if request.user.is_authenticated:
            totalitem = Cart.objects.filter(user=request.user).count()
            item_already_in_cart = Cart.objects.filter(
                product=product, user=request.user
            ).exists()

        return render(
            request,
            "app/products/productdetail.html",
            {
                "product": product,
                "product_variation": product_variation,
                "availability": availability,
                "item_already_in_cart": item_already_in_cart,
                "totalitem": totalitem,
            },
        )
# from payu.gateway import payu_url
# payu_url = payu_url()
# def pay_u(request):
#     payu_salt = "MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCv5l1SRpWHOr8YlmRP/2rf8v0chj8UH4rcljVyIk1DjgQQmoZU8zipKNrBKyI7tbmMCzwbu4MiIs2zxAFgxT3Pkw2jkb6FQkEUTGwLpk6xtb5udjMdKmFHAbevhjAiHAxqjtgKiycaAJZXWqQMq5l1MZYYXcy8bmzJv9z6kNaP9sxWfjUIi/ApoCGlcEOLjjKtITe4K4RVxDrBtflSmA3XP70u7ys31Y/XXgMzVgEaawiuFhd/u6SIit5khA0n2GiWNbrMxsMjVIUVaazFAlW2/CHtHC0l7rK9a+pZfSw4HG4z3Ol/9xRsN5MBCzhW6rcLQfyc6yawWganWKrzNKlVAgMBAAECggEAd35OPTtYDyK4eNKJ2NKR3wsqKXuFVH1NDyc3rY5h4JeUaVcgFIuaHUh0uy87NUbxgpKLReevYLw1834e1YeIwv+KD2lN/ScSIOD9sThMU2s8r7u6Y4DLzrn699F312Qohyb82sTHTmHBwBwCP90/BZ8m8Oyfzg5R9whQ7SMBr4//lMVQNGo7hShdySPwO4moGyjeUNN8YrOoXEirQCoPR0KZiWFrUzLB0+lpgBHy29nFt923xNK0cDd2v1xvLr0oyh7Uoe7y188X9yWerAQVTknVokqfqyS023fmuBloOmQWSUhclLanz+h5CY33TIcBWXN6qYXwTOHb+//VtAKoYQKBgQDdS0DKJ1d+yRGLhfE8tqaWy6YZJZzdE5e6eId0lEet655NleZom7zy2raavFkt9ern2XWVJTxBXybE/LGcf7e+djstgHiznpNXDYwgUWJzczMqgKyRgMfsl9DmYR/SXbl0Q/jqw0lTIOyl5TOOdookOmjwd9ielS5u8uDoG59WiQKBgQDLfJSlhsg3B1nEMJwtclHpuIvQobczqcpRYH4P8VO3/K+jzBnfybYP6/c9chAcas2kWsYyigCOVXdPffEM6iMAdgOKb5WMDjd9RAIQEszTIld3P1qOn1vktSh2Bff5lJQiv8ac5JmsNgV9BaE6b9E/UOjBjH7zYv5qNIvmT0IJbQKBgHB7b9NRbAfl7CUfUB+sN8Eugp8Fn1ZAPz9pRHDdbhHZUf3d0+AYSVKoGWlNk4bpGR4ASuQkqRwRYYN/bkg+IweM0UevpaqnT/1PxYon1AMa60cPYKgU7Yo1INn5RFOJkFqosj2iRgMbGS658hrX5h/EENMqF9GDwrZifi982uEBAoGABhxHmnDhskVWPL348qRsMUiJakpw5exDVw4+utvUV8IOxCxs2nuELBY55m52bWQHqNfQ+9OJEL0gSBLQGkMtqeXhVVbkdsA2ilxwc2sdG3n8hmgwn/fJGqUWAfVL7QK5MBHyNOPoeXNl1stEfCy/a9dSJf3CEiz21tmdGd1nbkECgYEA14Y+4tdEgvNUikvgYF+UASxyWhNeJmfprn66QbkbCy6TWVARGnT3iyd3SCaFBv7JcKoN3B3v3XelxNXjgl0bPug38QE+mBGTLH17v1mP+75rjAqHA/Zbvpk+ikecw1SJJnb6y5uMLyBAQnChn0x4DiddzovYe4PEs0IfraonUAk="
#     payu_key = "jeYZqv"
#     payu_client_id = "e56030dd235e57d3777785f13127894a38249a61eb8e6318c025319a2774a381"
#     payu_client_seceret = "cb75cbf45b0c12270c5c98569cdeadbd0adbfc0db25e3dc2cf86d379548749ce"
#     payu_mode = "TEST"

@login_required
def add_to_cart(request):
    """
    Add a product to the user's cart.
    """
    user = request.user
    product_id = request.GET.get("prod_id")

    if not product_id:
        return HttpResponse("No product ID provided", status=400)

    if not Cart.objects.filter(Q(product_id=product_id) & Q(user=user)).exists():
        product = get_object_or_404(Product, id=product_id)
        Cart(user=user, product=product).save()
        messages.success(request, "Product Added to Cart Successfully!")
    else:
        messages.info(request, "Product already in cart.")

    return redirect("/cart")


@login_required
def show_cart(request):
    """
    Display the cart with product details and total amount.
    """
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        cart = Cart.objects.filter(user=request.user)
        amount = sum(p.quantity * p.product.discounted_price for p in cart)
        shipping_amount = 70.0
        totalamount = amount + shipping_amount

        if cart.exists():
            return render(
                request,
                "app/cart/addtocart.html",
                {
                    "carts": cart,
                    "amount": amount,
                    "totalamount": totalamount,
                    "totalitem": totalitem,
                },
            )
        else:
            return render(request, "app/cart/emptycart.html", {"totalitem": totalitem})

    return render(request, "app/cart/emptycart.html", {"totalitem": totalitem})


@login_required
def update_cart(request, action):
    """
    Update cart quantities (increment or decrement).
    """
    if request.method == "GET":
        prod_id = request.GET.get("prod_id")

        if not prod_id:
            return HttpResponse("No product ID provided", status=400)

        cart_item = get_object_or_404(
            Cart, Q(product_id=prod_id) & Q(user=request.user)
        )

        if action == "plus":
            cart_item.quantity += 1
        elif action == "minus" and cart_item.quantity > 1:
            cart_item.quantity -= 1

        cart_item.save()

        amount = sum(
            p.quantity * p.product.discounted_price
            for p in Cart.objects.filter(user=request.user)
        )
        shipping_amount = 70.0
        data = {
            "quantity": cart_item.quantity,
            "amount": amount,
            "totalamount": amount + shipping_amount,
        }
        return JsonResponse(data)

    return HttpResponse("Invalid request method", status=405)


@login_required
def remove_cart(request):
    """
    Remove a product from the cart.
    """
    if request.method == "GET":
        prod_id = request.GET.get("prod_id")
        cart_item = get_object_or_404(Cart, Q(product=prod_id) & Q(user=request.user))
        cart_item.delete()

        amount = sum(
            p.quantity * p.product.discounted_price
            for p in Cart.objects.filter(user=request.user)
        )
        shipping_amount = 70.0
        data = {
            "amount": amount,
            "totalamount": amount + shipping_amount,
        }
        return JsonResponse(data)

    return HttpResponse("")


@login_required
def checkout(request):
    """
    Checkout view to display addresses and cart items.
    """
    user = request.user
    addresses = Address.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    amount = sum(p.quantity * p.product.discounted_price for p in cart_items)
    shipping_amount = 70.0
    totalamount = amount + shipping_amount

    return render(
        request,
        "app/cart/checkout.html",
        {"addresses": addresses, "cart_items": cart_items, "totalamount": totalamount},
    )


def generate_receipt(order_id, response_data):
    print("\n\n\nCreating the Transaction History")
    try:
        filtered_orders = OrderPlaced.objects.filter(order_id=order_id)
        first_order = filtered_orders.first()
        order_date = first_order.ordered_date
        date = order_date.strftime('%Y-%m-%d %H:%M:%S %Z')
        shipping_address = first_order.address
    except ObjectDoesNotExist:
        return None, None

    if response_data:
        total_cost = response_data.get("amount")
        status_id = response_data.get("status_id")
        status = response_data.get("status")

    # Prepare receipt data for successful transactions
    receipt_data = {
        "shipping_address": {
            "Full Name": shipping_address.full_name,
            "Locality": shipping_address.locality,
            "City": shipping_address.city,
            "State": shipping_address.state,
            "ZipCode": shipping_address.zipcode,
            "Mobile Number": shipping_address.mobile_number,
            "Land Mark": shipping_address.land_mark,
        },
        "order_items": [],
        "order_date": date,
        "total": total_cost,
        "status": status,
    }

    for order_item in filtered_orders:
        product = order_item.product
        product_details = {
            "Title": product.title,
            "Quantity": order_item.quantity,
            "Selling Price": product.selling_price,
            "Discounted Price": product.discounted_price,
            "Brand": product.brand,
        }
        receipt_data["order_items"].append(product_details)

    # Prepare transaction data
    transaction_data = {
        "status": status,
        "order": first_order,
        "shipping_address": str(receipt_data["shipping_address"]),
        "order_date": order_date,
        "total_cost": total_cost,
        "order_items": receipt_data["order_items"],
        "txn_id": response_data.get("txn_id"),
        "payment_method_type": response_data.get("payment_method_type"),
        "merchant_id": response_data.get("merchant_id"),
        "txn_uuid": response_data.get("txn_uuid"),
        "gateway": response_data.get("txn_detail", {}).get("gateway", ""),
    }

    # If the payment method is CARD, extract card details
    if response_data.get("payment_method_type") == "CARD":
        card_details = {
            "expiry_year": response_data.get("card", {}).get("expiry_year"),
            "expiry_month": response_data.get("card", {}).get("expiry_month"),
            "name_on_card": response_data.get("card", {}).get("name_on_card"),
            "card_issuer": response_data.get("card", {}).get("card_issuer"),
            "last_four_digits": response_data.get("card", {}).get("last_four_digits"),
            "card_type": response_data.get("card", {}).get("card_type"),
            "card_brand": response_data.get("card", {}).get("card_brand"),
            "card_issuer_country": response_data.get("card", {}).get("card_issuer_country"),
        }
        transaction_data["card_details"] = card_details

    # Save transaction to the database for successful payments
    transaction = Transaction.objects.create(
        order=first_order,
        status=transaction_data["status"],
        status_id=status_id,
        shipping_address=transaction_data["shipping_address"],
        order_date=transaction_data["order_date"],
        total_cost=transaction_data["total_cost"],
        order_items=transaction_data["order_items"],
        txn_id=transaction_data["txn_id"],
        payment_method_type=transaction_data["payment_method_type"],
        merchant_id=transaction_data["merchant_id"],
        txn_uuid=transaction_data["txn_uuid"],
        gateway=transaction_data["gateway"],
        card_details=transaction_data.get("card_details", {})
    )

    return receipt_data

@csrf_exempt
def payment_done(request):
    try:
        response_data = request.POST.dict()
        logger.info(f"\n\nReceived payment completion request: {json.dumps(response_data, indent=4)}")

        order_id = response_data.get("order_id")
        status = response_data.get("status")
        signature = response_data.get("signature")
        signature_algorithm = response_data.get("signature_algorithm")
        status_id = response_data.get("status_id")

        order_placed_data = OrderPlaced.objects.filter(order_id=order_id).first()
        order_status_response = check_order_status(order_id, str(order_placed_data.customer.id))

        if not all([order_id, status, signature]):
            logger.info("\nMissing required fields in payment completion request.")
            return JsonResponse({"error": "Missing required fields"}, status=400)

        params = {
            "signature": signature,
            "order_id": order_id,
            "status": status,
            "signature_algorithm": signature_algorithm,
            "status_id": status_id
        }

        # Extract desired parameters
        api_secret = settings.API_SECRET
        relevant_params = {k: v for k, v in params.items() if k not in ("signature", "signature_algorithm")}
        encoded_sorted = []
        for key in sorted(relevant_params.keys()):
            encoded_key = urllib.parse.quote_plus(key)
            encoded_value = urllib.parse.quote_plus(relevant_params[key])
            encoded_sorted.append(f"{encoded_key}={encoded_value}")

        encoded_string = urllib.parse.quote_plus("&".join(encoded_sorted))
        dig = hmac.new(api_secret.encode('utf-8'), encoded_string.encode('utf-8'), digestmod=hashlib.sha256).digest()
        expected_signature = base64.b64encode(dig).decode()

        if signature != expected_signature:
            logger.info("Signature mismatch")
            return JsonResponse({"error": "Invalid signature"}, status=400)

        if status_id == "21":
            try:
                orders = OrderPlaced.objects.filter(order_id=order_id)
                generate_receipt(order_id, order_status_response)
                logger.info(f"\n\nReceipt generated for order {order_id}.")

                if orders.exists():
                    for order in orders:
                        order.status = "Accepted"
                        order.save()
                    return process_cart_items(order.user, order_id)

            except OrderPlaced.DoesNotExist:
                return JsonResponse({"error": "Order not found"}, status=404)

        elif status_id in ["26", "27", "23"]:
            orders = OrderPlaced.objects.filter(order_id=order_id)
            order_status_response
            generate_receipt(order_id, order_status_response)
            # Handle failed transaction
            logger.info(f"Transaction failed for order {order_id}.")\
            
            return render(request, "app/paymentfailed.html", {
                "status_message": "Transaction failed. Please check your payment details and try again."
            })

        elif status_id in ["20", "36", "37", "23"]:
            # Handle special statuses
            logger.info(f"Transaction in special status for order {order_id}.")

            context = {
                "status_message": {
                    "20": "Transaction has started. Please wait for confirmation.",
                    "36": "Transaction has been auto-refunded.",
                    "37": "Transaction has been partially charged.",
                    "23": "Authentication is in progress",
                }.get(status_id, "Unknown status.")
            }
            return render(request, "app/paymentfailed.html", context)

        else:
            logger.info("Invalid or unrecognized status ID.")
            return render(request, "app/paymentfailed.html")

    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)


def check_order_status(order_id, customer_id):
    """
    Check the order status from HDFC API.

    Args:
        order_id (str): The ID of the order to check.
        customer_id (str): The customer ID for the request.

    Returns:
        dict: The response JSON from the HDFC API.
    """
    # Encode API key in Base64
    encoded_credentials = base64.b64encode(
        f"{settings.HDFC_API_KEY}:".encode()
    ).decode()

    url = f"https://smartgatewayuat.hdfcbank.com/orders/{order_id}"

    # Set headers
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "version": "2023-06-30",
        "Content-Type": "application/x-www-form-urlencoded",
        "x-merchantid": settings.HDFC_MERCHANT_ID,
        "x-customerid": customer_id,
    }

    # Make the GET request
    response = requests.get(url, headers=headers)

    # Log the response
    if response.status_code == 200:
        response_json = response.json()
        logger.info("\n#####start################## \tStatus Order API\n")
        logger.info(f"Order {order_id} status updated to: {json.dumps(response_json, indent=4)}")
        logger.info("\n\n#####end################## \tStatus Order API\n")
        return response_json
    else:
        logger.info(f"Failed to retrieve order status: {response.status_code} - {response.text}")
        return None


def process_cart_items(user, order_id):
    """
    Fetch cart items for the user and create orders.
    """
    try:
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            logger.info(f"\n\nNo cart items found for user {user.id}.")
            return JsonResponse({"message": "No cart items found"}, status=404)

        for cart_item in cart_items:
            cart_item.delete()
            logger.info(f"\n\nDeleted cart item {cart_item.id} for user {user.id}.")

        logger.info(f"\n\nAll cart items processed and deleted for order {order_id}.")

        return redirect("orders")

    except Exception as e:
        logger.error(f"An error occurred while processing cart items: {str(e)}")
        return JsonResponse({"message": f"An error occurred: {str(e)}"}, status=500)


@login_required
def orders(request):
    """
    View to display all orders placed by the user and check their status.
    """
    updated_orders = False
    updated_order_id = None

    try:
        user_id = request.user.id
        logger.info(f"\n\nUser {user_id} is requesting their orders.")

        # Retrieve orders for the user
        order_placed = OrderPlaced.objects.filter(user=request.user).order_by('-ordered_date')

        if order_placed.exists():
            for order in order_placed:
                if order.status == "Pending":
                    order_status_response = check_order_status(order.order_id, str(user_id))
                    if order_status_response:
                        bank_status_id = order_status_response.get("status_id")
                        complete_order_id = order_status_response.get("order_id")
                        if bank_status_id == 21:
                            order.status = "Accepted"
                            order.save()
                            updated_orders = True
                            updated_order_id = order.order_id
                            generate_receipt(order.order_id, order_status_response)
                            logger.info(f"\n\nOrder {order.order_id} status updated to 'Accepted'.")
                            process_cart_items(request.user, order.order_id) 

                    elif bank_status_id in ["26", "27"]:
                        order.status = "Failed"
                        order.save()
                        logger.info(f"\n\nOrder {order.order_id} status updated to 'Failed' due to authentication/authorization issues.")

                    else:
                        logger.info(f"\n\nOrder {order.order_id} has unrecognized status (status ID: {bank_status_id}).")

        else:
            logger.info(f"\n\nNo orders found for user {user_id}.")

        # Render the orders page
        return render(request, "app/cart/orders.html", {
            "order_placed": order_placed,
            "updated_orders": updated_orders,
            "updated_order_id": updated_order_id,
        })

    except Exception as e:
        logger.error(f"An error occurred while retrieving orders for user {user_id}: {str(e)}")
        return render(request, "app/cart/orders.html", {"order_placed": [], "updated_orders": False, "updated_order_id": None})

from django.http import HttpResponse

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from weasyprint import HTML

@login_required
def get_transaction(request, order_id):
    # Fetch the transaction
    prefix = "SG988-"
    postfix = "-1"
    
    # Construct the full order_id
    full_order_id = f"{prefix}{order_id}{postfix}"
    transaction = get_object_or_404(Transaction, txn_id=full_order_id) 

    logger.info("Transaction Data: %s", transaction.__dict__)
    transaction_dict = transaction.__dict__.copy()
    transaction_dict['shipping_address'] = ast.literal_eval(transaction_dict['shipping_address'])

    for item in transaction_dict['order_items']:
        if 'Selling Price' in item:
            item['selling_price'] = f"₹{item.pop('Selling Price'):.2f}"
        if 'Discounted Price' in item:
            item['discounted_price'] = f"₹{item.pop('Discounted Price'):.2f}"

    html_string = render_to_string('app/cart/receipt_template.html', {'transaction': transaction_dict})

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{transaction.txn_id}.pdf"'

    # Generate PDF from the HTML string
    HTML(string=html_string).write_pdf(response)

    return response

@login_required
@require_GET
def get_transaction_json(request, order_id):
    # Fetch the transaction
    prefix = "SG988-"
    postfix = "-1"
    
    # Construct the full order_id
    full_order_id = f"{prefix}{order_id}{postfix}"

    transaction = get_object_or_404(Transaction, txn_id=full_order_id)

    # Prepare the data to return as JSON
    transaction_dict = {
        'id': transaction.id,
        'status': transaction.status,
        'status_id': transaction.status_id,
        'order_id': transaction.order_id,
        'shipping_address': ast.literal_eval(transaction.shipping_address),
        'order_date': transaction.order_date.isoformat(),
        'total_cost': transaction.total_cost,
        'order_items': [
            {
                'title': item['Title'],
                'quantity': item['Quantity'],
                'selling_price': f"₹{item['Selling Price']:.2f}",
                'discounted_price': f"₹{item['Discounted Price']:.2f}",
                'brand': item['Brand']
            }
            for item in transaction.order_items
        ],
        'txn_id': transaction.txn_id,
        'payment_method_type': transaction.payment_method_type,
        'merchant_id': transaction.merchant_id,
        'txn_uuid': transaction.txn_uuid,
        'gateway': transaction.gateway,
        'card_details': transaction.card_details,
    }

    return JsonResponse(transaction_dict)

class CustomerRegistrationView(View):
    """
    View to handle customer registration.
    """

    def get(self, request):
        form = CustomerRegistrationForm()
        return render(
            request, "app/authentication/customerregistration.html", {"form": form}
        )

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, "Congratulations! Registered Successfully.")
                return redirect("home")
        return render(
            request, "app/authentication/customerregistration.html", {"form": form}
        )


@method_decorator(login_required, name="dispatch")
class ProfileView(View):
    """
    View to manage customer profile and addresses.
    """

    def get(self, request):
        totalitem = Cart.objects.filter(user=request.user).count()
        customer = Customer.objects.filter(user=request.user).first()
        form = (
            CustomerProfileForm(instance=customer)
            if customer
            else CustomerProfileForm()
        )
        addresses = Address.objects.filter(user=request.user)

        return render(
            request,
            "app/profile/profile.html",
            {
                "form": form,
                "customer": customer,
                "addresses": addresses,
                "active": "btn-primary",
                "totalitem": totalitem,
            },
        )

    def post(self, request):
        totalitem = Cart.objects.filter(user=request.user).count()
        customer = Customer.objects.filter(user=request.user).first()
        form = CustomerProfileForm(request.POST, request.FILES, instance=customer)

        if form.is_valid():
            customer = form.save(commit=False)
            customer.user = request.user
            customer.save()
            messages.success(request, "Congratulations! Profile Updated Successfully.")
            return redirect("profile")

        return render(
            request,
            "app/profile/profile.html",
            {
                "form": form,
                "customer": customer,
                "active": "btn-primary",
                "totalitem": totalitem,
            },
        )


@login_required
def address_view(request):
    """
    View to manage addresses for the user.
    """
    user = request.user
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = user
            address.save()
            messages.success(request, "New Address Added Successfully.")
            return redirect("address")
    else:
        form = AddressForm()

    addresses = Address.objects.filter(user=user)
    return render(
        request, "app/profile/address.html", {"form": form, "addresses": addresses}
    )


def terms_conditions(request):
    """
    View to display terms and conditions.
    """
    return render(request, "app/policy/conditions.html")


def privacy(request):
    """
    View to display privacy policy.
    """
    return render(request, "app/policy/privacy.html")


def men_collection(request):
    """
    View to list men's wear products with pagination.
    """
    mens_wear = Product.objects.filter(category="MW")
    paginator = Paginator(mens_wear, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "app/products/men_collection.html", {"page_obj": page_obj})


def women_collection(request):
    """
    View to list women's wear products with pagination.
    """
    womens_wear = Product.objects.filter(category="WW")
    paginator = Paginator(womens_wear, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "app/products/women_collection.html", {"page_obj": page_obj})


def user_logout(request):
    logout(request)
    return redirect("login")


@csrf_exempt
def search_products(request):
    if request.method == "GET":
        search_term = request.GET.get("name", "")
        min_price = request.GET.get("min_price", "")
        max_price = request.GET.get("max_price", "")

        products = Product.objects.all()

        if search_term:
            products = products.filter(title__icontains=search_term)

        if min_price:
            products = products.filter(selling_price__gte=min_price)

        if max_price:
            products = products.filter(selling_price__lte=max_price)

        product_list = list(
            products.values(
                "id",
                "title",
                "selling_price",
                "discounted_price",
                "description",
                "brand",
                "category",
                "product_image",
            )
        )

        return JsonResponse(product_list, safe=False)
# from .payu import initiate_payment_payu

@login_required
def initiate_payment(request):
    """
    Initiate payment with HDFC.
    """
    user = request.user
    cart_items = Cart.objects.filter(user=user)

    if not cart_items.exists():
        logger.info(
            f"User {user.id} has no cart items. Redirecting to empty cart response."
        )
        return JsonResponse({"message": "No cart items found"}, status=404)
    # payment_gateway = request.POST.get('gateway')

    # Fetch customer details
    customer = Customer.objects.filter(user=user).first()

    # Check if customer details are available
    if not customer:
        logger.info(
            f"User {user.id} does not have profile details. Redirecting to profile page."
        )
        messages.info(
            request,
            "Please fill out your profile details to continue with the payment.",
        )
        return redirect("profile")

    amount = sum(p.quantity * p.product.discounted_price for p in cart_items)
    shipping_amount = 70.0
    totalamount = amount + shipping_amount

    order_id = f"order-{uuid.uuid4()}"

    selected_address_id = request.POST.get('custid')
    selected_address = Address.objects.get(id=selected_address_id)

    for cart_item in cart_items:
        OrderPlaced.objects.create(
            user=user,
            customer=Customer.objects.get(user=user),
            product=cart_item.product,
            quantity=cart_item.quantity,
            status="Pending",
            order_id=order_id,
            address=Address.objects.get(id=selected_address_id)
        )

    logger.info(f"\n\nOrder {order_id} created with total amount {totalamount}")

    payload = {
        "order_id": order_id,
        "amount": str(totalamount),
        "customer_id": str(user.id),
        "customer_email": str(user.email),
        "customer_phone": str(customer.mobile_number),
        "payment_page_client_id": settings.HDFC_CLIENT_ID,
        "action": "paymentPage",
        "currency": "INR",
        "return_url": request.build_absolute_uri("/paymentdone/"),
        "description": "Complete your payment",
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "shipping_address": f"{selected_address.full_name}, {selected_address.locality}, {selected_address.city}, {selected_address.state} - {selected_address.zipcode}",
    }

    logger.info(f"\n\nSending request to HDFC: {json.dumps(payload, indent=4)}")
    # Prepare headers
    api_key = settings.HDFC_API_KEY
    merchant_id = settings.HDFC_MERCHANT_ID
    encoded_credentials = base64.b64encode(f"{api_key}:".encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/json",
        "x-merchantid": merchant_id,
        "x-customerid": str(user.id),
    }

    # Send request to HDFC
    try:
        response = requests.post(
            "https://smartgatewayuat.hdfcbank.com/session",
            json=payload,
            headers=headers,
        )
        response.raise_for_status()  # Raises HTTPError for bad responses
        response_data = response.json()
        logger.info(f"\n\nResponse after request from gateway: {json.dumps(response_data, indent=4)}")

        payment_url = response_data.get("payment_links", {}).get("web", "")

        if payment_url:
            logger.info(f"\n\nPayment URL generated: {payment_url}")
            return redirect(payment_url)
        else:
            logger.info(
                f"Payment response did not contain a payment URL: {response_data}"
            )
            return JsonResponse(
                {"error": "Payment initiation failed", "response": response_data},
                status=400,
            )

    except requests.RequestException as e:
        logger.info(f"\n\nPayment initiation request failed: {str(e)}")
        return JsonResponse(
            {"error": "Payment initiation failed", "details": str(e)}, status=500
        )
