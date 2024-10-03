import random
import logging
import base64
import requests
import hashlib
import hmac
import urllib.parse
import json
from django.contrib import messages
from django.contrib.auth import authenticate, login ,logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .forms import CustomerProfileForm, CustomerRegistrationForm, AddressForm
from .models import Cart, Customer, OrderPlaced, Product, ProductVariation, Address
from django.conf import settings
logger = logging.getLogger('app')



@method_decorator(csrf_exempt, name='dispatch')
class ProductView(View):
    def get(self, request):
        totalitem = 0
 
        mens_wear = list(Product.objects.filter(category="MW"))
        womens_wear = list(Product.objects.filter(category="WW"))
 
        # Combine and shuffle products
        combined_products = mens_wear + womens_wear
        random.shuffle(combined_products)
 
        # Paginate products
        paginator = Paginator(combined_products, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
 
        if request.user.is_authenticated:
            totalitem = Cart.objects.filter(user=request.user).count()
 
        return render(
            request,
            "app/index.html",
            {
                "page_obj": page_obj,
                "totalitem": totalitem,
            }
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
            item_already_in_cart = Cart.objects.filter(product=product, user=request.user).exists()

        return render(
            request,
            "app/products/productdetail.html",
            {
                "product": product,
                "product_variation": product_variation,
                "availability": availability,
                "item_already_in_cart": item_already_in_cart,
                "totalitem": totalitem,
            }
        )

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
                }
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

        cart_item = get_object_or_404(Cart, Q(product_id=prod_id) & Q(user=request.user))
        
        if action == "plus":
            cart_item.quantity += 1
        elif action == "minus" and cart_item.quantity > 1:
            cart_item.quantity -= 1
        
        cart_item.save()

        amount = sum(p.quantity * p.product.discounted_price for p in Cart.objects.filter(user=request.user))
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
        
        amount = sum(p.quantity * p.product.discounted_price for p in Cart.objects.filter(user=request.user))
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
    if request.method == "POST":
        return redirect('initiate-payment')

    user = request.user
    addresses = Address.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    amount = sum(p.quantity * p.product.discounted_price for p in cart_items)
    shipping_amount = 70.0
    totalamount = amount + shipping_amount

    return render(
        request,
        "app/cart/checkout.html",
        {"addresses": addresses, "cart_items": cart_items, "totalamount": totalamount}
    )


@csrf_exempt
def payment_done(request):
    """
    Handle the payment completion and create orders as an API endpoint.
    """
    try:
        # Log incoming request data
        response_data = request.POST.dict()
        logger.info(f"Received payment completion request: {json.dumps(response_data)}")

        order_id = response_data.get("order_id")
        status = response_data.get("status")
        signature = response_data.get("signature")
        signature_algorithm = response_data.get("signature_algorithm")
        status_id = response_data.get("status_id")

        if not all([order_id, status, signature]):
            logger.warning("Missing required fields in payment completion request.")
            return JsonResponse({"error": "Missing required fields"}, status=400)

        params = {
            "order_id": order_id,
            "status": status,
            "status_id": status_id
        }

        encoded_sorted = []
        for key in sorted(params.keys()):
            encoded_sorted.append(
                urllib.parse.quote_plus(key) + '=' + urllib.parse.quote_plus(params[key])
            )

        signature_string = '&'.join(encoded_sorted)
        encoded_string = urllib.parse.quote_plus(signature_string)

        # Verify the HMAC signature
        api_secret = settings.API_SECRET
        if not api_secret:
            logger.error("API secret not found in settings.")
            return JsonResponse({"error": "Internal server error"}, status=500)

        dig = hmac.new(api_secret.encode(), msg=encoded_string.encode(), digestmod=hashlib.sha256).digest()
        expected_signature = urllib.parse.quote_plus(base64.b64encode(dig).decode())

        if signature != expected_signature:
            logger.warning(f"Signature mismatch. Expected: {expected_signature}, Received: {signature}")
            return JsonResponse({"error": "Invalid signature"}, status=400)

        if status_id == "21":
            # Update the order status to "Accepted" if status_id is "21"
            try:
                orders = OrderPlaced.objects.filter(order_id=order_id)
                if orders.exists():
                    for order in orders:
                        order.status = "Accepted"
                        order.save()
                        logger.info(f"Order {order_id} status updated to 'Accepted'.")

            except OrderPlaced.DoesNotExist:
                logger.error(f"Order with ID {order_id} not found.")
                return JsonResponse({"error": "Order not found"}, status=404)
        else:
            logger.warning(f"Invalid status_id received: {status_id}.")
            return JsonResponse({"error": "Invalid status_id"}, status=400)

        # Process cart items and create orders
        return process_cart_items(request.user, order_id)

    except Exception as e:
        logger.error(f"An error occurred while handling payment completion: {str(e)}")
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)



def process_cart_items(user, order_id):
    """
    Fetch cart items for the user, create orders, and delete cart items.
    """
    try:
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            logger.warning(f"No cart items found for user {user.id}.")
            return JsonResponse({"message": "No cart items found"}, status=404)

        for cart_item in cart_items:
            cart_item.delete()
            logger.info(f"Deleted cart item {cart_item.id} for user {user.id}.")

        logger.info(f"All cart items processed and deleted for order {order_id}.")
        return redirect('orders')

    except Exception as e:
        logger.error(f"An error occurred while processing cart items: {str(e)}")
        return JsonResponse({"message": f"An error occurred: {str(e)}"}, status=500)


@login_required
def orders(request):
    """
    View to display all orders placed by the user.
    """
    try:
        # Log user ID and action
        user_id = request.user.id
        logger.info(f"User {user_id} is requesting their orders.")

        # Retrieve orders for the user
        order_placed = OrderPlaced.objects.filter(user=request.user)
        
        if order_placed.exists():
            logger.info(f"Found {order_placed.count()} orders for user {user_id}.")
        else:
            logger.info(f"No orders found for user {user_id}.")

        # Render the orders page
        return render(request, "app/cart/orders.html", {"order_placed": order_placed})
    
    except Exception as e:
        logger.error(f"An error occurred while retrieving orders for user {user_id}: {str(e)}")
        return render(request, "app/cart/orders.html", {"order_placed": []})  # Render with empty list on error

class CustomerRegistrationView(View):
    """
    View to handle customer registration.
    """
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, "app/authentication/customerregistration.html", {"form": form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, "Congratulations! Registered Successfully.")
                return redirect('home')
        return render(request, "app/authentication/customerregistration.html", {"form": form})


@method_decorator(login_required, name="dispatch")
class ProfileView(View):
    """
    View to manage customer profile and addresses.
    """
    def get(self, request):
        totalitem = Cart.objects.filter(user=request.user).count()
        customer = Customer.objects.filter(user=request.user).first()
        form = CustomerProfileForm(instance=customer) if customer else CustomerProfileForm()
        addresses = Address.objects.filter(user=request.user)

        return render(
            request,
            "app/profile/profile.html",
            {
                "form": form,
                "customer": customer,
                "addresses": addresses,
                "active": "btn-primary",
                "totalitem": totalitem
            }
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
            return redirect('profile')

        return render(
            request,
            "app/profile/profile.html",
            {
                "form": form,
                "customer": customer,
                "active": "btn-primary",
                "totalitem": totalitem
            }
        )


@login_required
def address_view(request):
    """
    View to manage addresses for the user.
    """
    user = request.user
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = user
            address.save()
            messages.success(request, "New Address Added Successfully.")
            return redirect('address')
    else:
        form = AddressForm()

    addresses = Address.objects.filter(user=user)
    return render(request, 'app/profile/address.html', {'form': form, 'addresses': addresses})


def terms_conditions(request):
    """
    View to display terms and conditions.
    """
    return render(request, 'app/policy/conditions.html')


def privacy(request):
    """
    View to display privacy policy.
    """
    return render(request, 'app/policy/privacy.html')


def men_collection(request):
    """
    View to list men's wear products with pagination.
    """
    mens_wear = Product.objects.filter(category="MW")
    paginator = Paginator(mens_wear, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'app/products/men_collection.html', {"page_obj": page_obj})


def women_collection(request):
    """
    View to list women's wear products with pagination.
    """
    womens_wear = Product.objects.filter(category="WW")
    paginator = Paginator(womens_wear, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'app/products/women_collection.html', {"page_obj": page_obj})

def user_logout(request):
    logout(request)
    return redirect('login')



@csrf_exempt
def search_products(request):
    if request.method == 'GET':
        search_term = request.GET.get('name', '')
        min_price = request.GET.get('min_price', '')
        max_price = request.GET.get('max_price', '')

        products = Product.objects.all()

        if search_term:
            products = products.filter(title__icontains=search_term)
        
        if min_price:
            products = products.filter(selling_price__gte=min_price)
        
        if max_price:
            products = products.filter(selling_price__lte=max_price)
        
        product_list = list(products.values('id', 'title', 'selling_price', 'discounted_price', 'description', 'brand', 'category', 'product_image'))

        return JsonResponse(product_list, safe=False)





@login_required
def initiate_payment(request):
    """
    Initiate payment with HDFC.
    """
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    
    if not cart_items.exists():
        logger.info(f"User {user.id} has no cart items. Redirecting to empty cart response.")
        return JsonResponse({"message": "No cart items found"}, status=404)
    
    # Fetch customer details
    customer = Customer.objects.filter(user=user).first()

    # Check if customer details are available
    if not customer:
        logger.info(f"User {user.id} does not have profile details. Redirecting to profile page.")
        messages.info(request, "Please fill out your profile details to continue with the payment.")
        return redirect('profile')

    amount = sum(p.quantity * p.product.discounted_price for p in cart_items)
    shipping_amount = 70.0
    totalamount = amount + shipping_amount

    order_id = f"order-{random.randint(1000, 9999)}"
    for cart_item in cart_items:
        OrderPlaced.objects.create(
            user=user,
            customer=Customer.objects.get(user=user),
            product=cart_item.product,
            quantity=cart_item.quantity,
            status="Pending",  # Here you may want to set an appropriate status
            order_id=order_id
        )

    logger.debug(f"Order {order_id} created with total amount {totalamount}")

    # Prepare data for HDFC API
    payload = {
        "order_id": order_id,  # Use the generated order_id
        "amount": str(totalamount),
        "customer_id": str(user.id),
        "customer_email": str(user.email),
        "customer_phone": str(customer.mobile_number),
        "payment_page_client_id": settings.HDFC_CLIENT_ID,
        "action": "paymentPage",
        "currency": "INR",
        "return_url": request.build_absolute_uri('/paymentdone/'),
        "description": "Complete your payment",
        "first_name": customer.first_name,
        "last_name": customer.last_name,
    }

    logger.debug(f"Sending request to HDFC: {json.dumps(payload)}")
    # Prepare headers
    api_key = settings.HDFC_API_KEY
    merchant_id = settings.HDFC_MERCHANT_ID
    encoded_credentials = base64.b64encode(f"{api_key}:".encode()).decode()

    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Content-Type': 'application/json',
        'x-merchantid': merchant_id,
        'x-customerid': str(user.id)
    }
    
    # Send request to HDFC
    try:
        response = requests.post('https://smartgatewayuat.hdfcbank.com/session', json=payload, headers=headers)
        response.raise_for_status()  # Raises HTTPError for bad responses
        response_data = response.json()
        
        payment_url = response_data.get('payment_links', {}).get('web', '')
        
        if payment_url:
            logger.info(f"Payment URL generated: {payment_url}")
            return redirect(payment_url)
        else:
            logger.error(f"Payment response did not contain a payment URL: {response_data}")
            return JsonResponse({'error': 'Payment initiation failed', 'response': response_data}, status=400)
    
    except requests.RequestException as e:
        logger.error(f"Payment initiation request failed: {str(e)}")
        return JsonResponse({'error': 'Payment initiation failed', 'details': str(e)}, status=500)


