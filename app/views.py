import random
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



@login_required
def payment_done(request):
    """
    Handle the payment completion and create orders.
    """
    user = request.user
    order_id = request.GET.get("order_id")
    if not order_id:
        return HttpResponse("Invalid order ID", status=400)

    cart_items = Cart.objects.filter(user=user)
    for cart_item in cart_items:
        OrderPlaced.objects.create(
            user=user,
            product=cart_item.product,
            quantity=cart_item.quantity,
            order_id=order_id
        )
        cart_item.delete()

    return redirect("orders")



@login_required
def orders(request):
    """
    View to display all orders placed by the user.
    """
    order_placed = OrderPlaced.objects.filter(user=request.user)
    return render(request, "app/cart/orders.html", {"order_placed": order_placed})


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


#-------------------------------------------------HDFC Payment GateWay----------
# views.py

# views.py

import base64
import requests
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
import json
@login_required
def initiate_payment(request):
    """
    Initiate payment with HDFC.
    """
    user = request.user
    email = request.user.email
    print("\n\n\t----request data ", user,email)
    cart_items = Cart.objects.filter(user=user)
    Customer_detail = Customer.objects.filter(user=user)

    amount = sum(p.quantity * p.product.discounted_price for p in cart_items)
    shipping_amount = 70.0
    totalamount = amount + shipping_amount

    # Prepare data for HDFC API
    order_id = f"order-{random.randint(1000, 9999)}"  # Generate a unique order ID
    customer = Customer.objects.filter(user=user).first()
    
    payload = {
        "order_id": order_id,
        "amount": str(totalamount),
        # "customer_id": user.id,
        "customer_id":  str(user.id),
        "customer_email": str(user.email),
        "customer_phone": str(customer.mobile_number),  # Ensure phone number is in user profile
        "payment_page_client_id": settings.HDFC_CLIENT_ID,
        "action": "paymentPage",
        "currency": "INR",
        # "return_url": request.build_absolute_uri('/paymentdone'),
        "return_url": 'https://shivayinternational.co',
        "description": "Complete your payment",
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "metadata.JUSPAY:gateway_reference_id": "payu_test",
    }
    """
    curl --location 'https://smartgatewayuat.hdfcbank.com/session' \
    --header 'Authorization: Basic base_64_encoded_api_key==' \
    --header 'Content-Type: application/json' \
    --header 'x-merchantid: merchant_id' \
    --header 'x-customerid: customer_id' \
    --header 'Authorization: Basic MjMzQTJBRjQ2REI0NTNCOTQ0Q0JBMUFCNDlGOTIyOg==' \
    --data-raw '{
        "order_id": " testing-order-one",
        "amount": "10.0",
        "customer_id": "testing-customer-one",
        "customer_email": "test@mail.com",
        "customer_phone": "8604613494",
        "payment_page_client_id": "your_client_id",
        "action": "paymentPage",
        "currency": "INR",
        "return_url": "https://shop.merchant.com",
        "description": "Complete your payment",
        "first_name": "John",
        "last_name": "wick"
        "metadata.JUSPAY:gateway_reference_id": "payu_test",
    }
    '
    """

    # Prepare headers
    api_key = settings.HDFC_API_KEY
    merchant_id = settings.HDFC_MERCHANT_ID
    encoded_credentials = base64.b64encode(f"{api_key}:".encode()).decode()
    print("\n\n\t--encode",encoded_credentials)

    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Content-Type': 'application/json',
        'x-merchantid': merchant_id,
        # 'x-customerid': user.username
        'x-customerid': str(user.id)
    }
    print("\n\n\t---Payload", payload)
    print("\n\n\t---headers", headers)
    # Send request to HDFC
    response = requests.post('https://smartgatewayuat.hdfcbank.com/session', json=payload, headers=headers)

    # Handle response
    if response.status_code == 200:
        response_data = response.json()
        print("\n\n\t---Response Data", response_data)
        payment_url = response_data['payment_links']['web']
        print("\n\n\t--Payment url", payment_url)
        return redirect(payment_url)
    else:
        # return response#.status_code
        return JsonResponse({'error': 'Payment initiation failed', 'status':response.status_code, 'response':response.json()}, status=response.status_code)

        # return JsonResponse({'error': 'Payment initiation failed'}, status=400)
