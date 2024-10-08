from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path

from app import api_views, views

from .forms import (
    LoginForm,
    MyPasswordChangeForm,
    MyPasswordResetForm,
    MySetPasswordForm,
)

# Define URL patterns for the main app
urlpatterns = [
    # Product Views
    path("", views.ProductView.as_view(), name="home"),
    path(
        "product-detail/<int:pk>/",
        views.ProductDetailView.as_view(),
        name="product-detail",
    ),
    # Cart Actions
    path("add-to-cart/", views.add_to_cart, name="add-to-cart"),
    path("cart/", views.show_cart, name="showcart"),
    path("pluscart/", views.update_cart, {"action": "plus"}, name="pluscart"),
    path("minuscart/", views.update_cart, {"action": "minus"}, name="minuscart"),
    path("removecart/", views.remove_cart, name="removecart"),
    # Checkout and Orders
    path("checkout/", views.checkout, name="checkout"),
    path("orders/", views.orders, name="orders"),
    path("paymentdone/", views.payment_done, name="paymentdone"),
    # Profile and Address
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("address/", views.address_view, name="address"),
    # Collection Views
    path("men_collection/", views.men_collection, name="men_collection"),
    path("women_collection/", views.women_collection, name="women_collection"),
    # Static Pages
    path("terms-conditions/", views.terms_conditions, name="terms-conditions"),
    path("privacy/", views.privacy, name="privacy"),
    path("api/search/", views.search_products, name="search-products"),
]

# Define URL patterns for authentication views
auth_urls = [
    path(
        "accounts/login/",
        views.CustomLoginView.as_view(),
        name="login",
    ),
    path("accounts/logout/", views.user_logout, name="logout"),
    path(
        "passwordchange/",
        auth_views.PasswordChangeView.as_view(
            template_name="app/authentication/passwordchange.html",
            form_class=MyPasswordChangeForm,
            success_url="/passwordchangedone/",
        ),
        name="passwordchange",
    ),
    path(
        "passwordchangedone/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="app/authentication/passwordchangedone.html"
        ),
        name="passwordchangedone",
    ),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="app/authentication/password_reset.html",
            form_class=MyPasswordResetForm,
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="app/authentication/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="app/authentication/password_reset_confirm.html",
            form_class=MySetPasswordForm,
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="app/authentication/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path(
        "registration/",
        views.CustomerRegistrationView.as_view(),
        name="customerregistration",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("initiate-payment/", views.initiate_payment, name="initiate-payment"),
    path('transaction/<int:order_id>', views.get_transaction, name='get-transaction'),

]

# Define URL patterns for API views
api_urls = [
    path("api/company/", api_views.company_detail_api, name="company-detail-api"),
    path("api/carousel/", api_views.latest_and_discount_product, name="carousel"),
    path(
        "api/address/<int:id>/update/",
        api_views.update_address,
        name="api-update-address",
    ),
    path(
        "api/address/<int:id>/delete/",
        api_views.delete_address,
        name="api-delete-address",
    ),
    path(
        "api/address/set-active/",
        api_views.set_active_address,
        name="set-active-address",
    ),
    path("api/products/", api_views.ProductListAPIView.as_view(), name="product-list"),
]

# Combine all URL patterns
urlpatterns += auth_urls
urlpatterns += api_urls

# Serve media files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
