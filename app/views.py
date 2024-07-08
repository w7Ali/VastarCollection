from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import HttpResponse, get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth import authenticate#, login

from .forms import CustomerProfileForm, CustomerRegistrationForm, AddressForm
from .models import Cart, Customer, OrderPlaced, Product, ProductVariation, Address


class ProductView(View):
    def get(self, request):
        totalitem = 0
        mens_wear = Product.objects.filter(category="MW")
        womens_wear = Product.objects.filter(category="WW")
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(
            request,
            "app/home.html",
            {
                "mens_wear": mens_wear,
                "womens_wear": womens_wear,
            },
        )


class ProductDetailView(View):
    def get(self, request, pk):
        totalitem = 0
        product = get_object_or_404(Product, pk=pk)

        # Check if there is a ProductVariation for the product
        try:
            product_variation = ProductVariation.objects.filter(product=product)
            availability = True
        except ProductVariation.DoesNotExist:
            product_variation = None
            availability = False

        item_already_in_cart = False
        if request.user.is_authenticated:
            totalitem = Cart.objects.filter(user=request.user).count()
            item_already_in_cart = Cart.objects.filter(
                product=product, user=request.user
            ).exists()

        return render(
            request,
            "app/productdetail.html",
            {
                "product": product,
                "product_variation": product_variation,
                "availability": availability,
                "item_already_in_cart": item_already_in_cart,
                "totalitem": totalitem,
            },
        )


@login_required()
def add_to_cart(request):
    user = request.user
    item_already_in_cart1 = False
    product = request.GET.get("prod_id")
    item_already_in_cart1 = Cart.objects.filter(
        Q(product=product) & Q(user=request.user)
    ).exists()
    if item_already_in_cart1 == False:
        product_title = Product.objects.get(id=product)
        Cart(user=user, product=product_title).save()
        messages.success(request, "Product Added to Cart Successfully !!")
        return redirect("/cart")
    else:
        return redirect("/cart")
        # Below Code is used to return to same page
        # return redirect(request.META['HTTP_REFERER'])


@login_required
def show_cart(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0.0
        shipping_amount = 70.0
        totalamount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        print(cart_product)
        if cart_product:
            for p in cart_product:
                tempamount = p.quantity * p.product.discounted_price
                amount += tempamount
            totalamount = amount + shipping_amount
            return render(
                request,
                "app/addtocart.html",
                {
                    "carts": cart,
                    "amount": amount,
                    "totalamount": totalamount,
                    "totalitem": totalitem,
                },
            )
        else:
            return render(request, "app/emptycart.html", {"totalitem": totalitem})
    else:
        return render(request, "app/emptycart.html", {"totalitem": totalitem})


def plus_cart(request):
    if request.method == "GET":
        prod_id = request.GET["prod_id"]
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = p.quantity * p.product.discounted_price
            # print("Quantity", p.quantity)
            # print("Selling Price", p.product.discounted_price)
            # print("Before", amount)
            amount += tempamount
            # print("After", amount)
        # print("Total", amount)
        data = {
            "quantity": c.quantity,
            "amount": amount,
            "totalamount": amount + shipping_amount,
        }
        return JsonResponse(data)
    else:
        return HttpResponse("")


def minus_cart(request):
    if request.method == "GET":
        prod_id = request.GET["prod_id"]
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity -= 1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = p.quantity * p.product.discounted_price
            # print("Quantity", p.quantity)
            # print("Selling Price", p.product.discounted_price)
            # print("Before", amount)
            amount += tempamount
            # print("After", amount)
        # print("Total", amount)
        data = {
            "quantity": c.quantity,
            "amount": amount,
            "totalamount": amount + shipping_amount,
        }
        return JsonResponse(data)
    else:
        return HttpResponse("")


@login_required
def checkout(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=request.user)
    amount = 0.0
    shipping_amount = 70.0
    totalamount = 0.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
        for p in cart_product:
            tempamount = p.quantity * p.product.discounted_price
            amount += tempamount
        totalamount = amount + shipping_amount
    return render(
        request,
        "app/checkout.html",
        {"add": add, "cart_items": cart_items, "totalcost": totalamount},
    )


@login_required
def payment_done(request):
    custid = request.GET.get("custid")
    print("Customer ID", custid)
    user = request.user
    cartid = Cart.objects.filter(user=user)
    customer = Customer.objects.get(id=custid)
    print(customer)
    for cid in cartid:
        OrderPlaced(
            user=user, customer=customer, product=cid.product, quantity=cid.quantity
        ).save()
        print("Order Saved")
        cid.delete()
        print("Cart Item Deleted")
    return redirect("orders")


def remove_cart(request):
    if request.method == "GET":
        prod_id = request.GET["prod_id"]
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = p.quantity * p.product.discounted_price
            # print("Quantity", p.quantity)
            # print("Selling Price", p.product.discounted_price)
            # print("Before", amount)
            amount += tempamount
            # print("After", amount)
        # print("Total", amount)
        data = {"amount": amount, "totalamount": amount + shipping_amount}
        return JsonResponse(data)
    else:
        return HttpResponse("")


@login_required
def orders(request):
    op = OrderPlaced.objects.filter(user=request.user)
    return render(request, "app/orders.html", {"order_placed": op})


def mobile(request, data=None):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    if data == None:
        mobiles = Product.objects.filter(category="M")
    elif data == "Redmi" or data == "Samsung":
        mobiles = Product.objects.filter(category="M").filter(brand=data)
    elif data == "below":
        mobiles = Product.objects.filter(category="M").filter(
            discounted_price__lt=10000
        )
    elif data == "above":
        mobiles = Product.objects.filter(category="M").filter(
            discounted_price__gt=10000
        )
    return render(
        request, "app/mobile.html", {"mobiles": mobiles, "totalitem": totalitem}
    )


class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, "app/customerregistration.html", {"form": form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            # Save the form data and create a new Customer instance
            user = form.save()
            # Authenticate the user
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            # Log in the user
            if user is not None:
                login(request, user)
                messages.success(request, "Congratulations!! Registered Successfully.")
                return redirect('home')  # Redirect to the home page after successful registration and login

        return render(request, "app/customerregistration.html", {"form": form})


@method_decorator(login_required, name="dispatch")
class ProfileView(View):
    def get(self, request):
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = Cart.objects.filter(user=request.user).count()

        # Fetch the first customer profile if multiple exist
        customer = Customer.objects.filter(user=request.user).first()
        if customer:
            form = CustomerProfileForm(instance=customer)
        else:
            form = CustomerProfileForm()
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
            },
        )

    def post(self, request):
        totalitem = Cart.objects.filter(user=request.user).count()
        try:
            customer = Customer.objects.get(user=request.user)
            form = CustomerProfileForm(request.POST, request.FILES, instance=customer)
        except Customer.DoesNotExist:
            form = CustomerProfileForm(request.POST, request.FILES)

        if form.is_valid():
            customer = form.save(commit=False)
            customer.user = request.user  # Assign the current user to the customer instance
            customer.save()
            messages.success(request, "Congratulations!! Profile Updated Successfully.")
            return redirect('profile')  # Redirect to avoid resubmission of form

        return render(
            request,
            "app/profile.html",
            {"form": form, "customer": customer, "active": "btn-primary", "totalitem": totalitem},
        )


@login_required
def address_view(request):
    user = request.user
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = user
            address.save()
            messages.success(request, "New Address Added Successfully.")
            return redirect('address')  # Redirect to address page after saving
        else:
            print(form.errors)  # Print form errors to debug

    else:
        form = AddressForm()
    addresses = Address.objects.filter(user=user)
    # active_address = addresses.filter(is_active=True).first()
    context = {
        'form': form,
        'addresses': addresses,
        # 'active_address': active_address,
    }
    return render(request, 'app/address.html', context)