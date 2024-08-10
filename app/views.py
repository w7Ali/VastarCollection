from django.contrib import messages
from django.contrib.auth import authenticate, login ,logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View
import random
from django.core.serializers import serialize
from django.http import JsonResponse
import random
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
 
        # Serialize product data to JSON
        all_products_json = serialize('json', combined_products)
 
        # Log the serialized data for debugging
        print("Serialized products data:", all_products_json)
 
        # Paginate products
        paginator = Paginator(combined_products, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
 
        if request.user.is_authenticated:
            totalitem = Cart.objects.filter(user=request.user).count()
 
        return render(
            request,
            "app/home.html",
            {
                "page_obj": page_obj,
                "allProducts": all_products_json,  # Pass serialized JSON data
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
            "app/productdetail.html",
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
    if not Cart.objects.filter(Q(product=product_id) & Q(user=user)).exists():
        product = get_object_or_404(Product, id=product_id)
        Cart(user=user, product=product).save()
        messages.success(request, "Product Added to Cart Successfully!")
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
                "app/addtocart.html",
                {
                    "carts": cart,
                    "amount": amount,
                    "totalamount": totalamount,
                    "totalitem": totalitem,
                }
            )
        else:
            return render(request, "app/emptycart.html", {"totalitem": totalitem})

    return render(request, "app/emptycart.html", {"totalitem": totalitem})


@login_required
def update_cart(request, action):
    """
    Update cart quantities (increment or decrement).
    """
    if request.method == "GET":
        prod_id = request.GET.get("prod_id")
        cart_item = get_object_or_404(Cart, Q(product=prod_id) & Q(user=request.user))
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

    return HttpResponse("")


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
    user = request.user
    addresses = Address.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    amount = sum(p.quantity * p.product.discounted_price for p in cart_items)
    shipping_amount = 70.0
    totalamount = amount + shipping_amount

    return render(
        request,
        "app/checkout.html",
        {"addresses": addresses, "cart_items": cart_items, "totalamount": totalamount}
    )


@login_required
def payment_done(request):
    """
    Handle the payment completion and create orders.
    """
    custid = request.GET.get("custid")
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    customer = get_object_or_404(Customer, id=custid)

    for cart_item in cart_items:
        OrderPlaced.objects.create(
            user=user,
            customer=customer,
            product=cart_item.product,
            quantity=cart_item.quantity
        )
        cart_item.delete()

    return redirect("orders")


@login_required
def orders(request):
    """
    View to display all orders placed by the user.
    """
    order_placed = OrderPlaced.objects.filter(user=request.user)
    return render(request, "app/orders.html", {"order_placed": order_placed})


class CustomerRegistrationView(View):
    """
    View to handle customer registration.
    """
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, "app/customerregistration.html", {"form": form})

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
        return render(request, "app/customerregistration.html", {"form": form})


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
            "app/profile.html",
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
            "app/profile.html",
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
    return render(request, 'app/address.html', {'form': form, 'addresses': addresses})


def terms_conditions(request):
    """
    View to display terms and conditions.
    """
    return render(request, 'app/conditions.html')


def privacy(request):
    """
    View to display privacy policy.
    """
    return render(request, 'app/privacy.html')


def men_collection(request):
    """
    View to list men's wear products with pagination.
    """
    mens_wear = Product.objects.filter(category="MW")
    paginator = Paginator(mens_wear, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'app/men_collection.html', {"page_obj": page_obj})


def women_collection(request):
    """
    View to list women's wear products with pagination.
    """
    womens_wear = Product.objects.filter(category="WW")
    paginator = Paginator(womens_wear, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'app/women_collection.html', {"page_obj": page_obj})

def user_logout(request):
    logout(request)
    return redirect('login')
