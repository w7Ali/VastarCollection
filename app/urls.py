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

urlpatterns = [
    # path('', views.home),
    path("", views.ProductView.as_view(), name="home"),
    # path('product-detail', views.product_detail, name='product-detail'),
    path(
        "product-detail/<int:pk>/",
        views.ProductDetailView.as_view(),
        name="product-detail",
    ),
    path("add-to-cart/", views.add_to_cart, name="add-to-cart"),
    path("cart/", views.show_cart, name="showcart"),
    path("pluscart/", views.plus_cart),
    path("minuscart/", views.minus_cart),
    path("removecart/", views.remove_cart),
    path("checkout/", views.checkout, name="checkout"),
    path('address/', views.address_view, name='address'),
    path("orders/", views.orders, name="orders"),
    path("paymentdone/", views.payment_done, name="paymentdone"),
    path("mobile/", views.mobile, name="mobile"),
    path("mobile/<slug:data>", views.mobile, name="mobiledata"),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(
            template_name="app/login.html", authentication_form=LoginForm
        ),
        name="login",
    ),
    # path('profile/', views.profile, name='profile'),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path(
        "passwordchange/",
        auth_views.PasswordChangeView.as_view(
            template_name="app/passwordchange.html",
            form_class=MyPasswordChangeForm,
            success_url="/passwordchangedone/",
        ),
        name="passwordchange",
    ),
    path(
        "passwordchangedone/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="app/passwordchangedone.html"
        ),
        name="passwordchangedone",
    ),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="app/password_reset.html", form_class=MyPasswordResetForm
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="app/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="app/password_reset_confirm.html",
            form_class=MySetPasswordForm,
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="app/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path(
        "registration/",
        views.CustomerRegistrationView.as_view(),
        name="customerregistration",
    ),
    path(
        "api/company/", api_views.company_detail_api, name="company-detail-api"
    ),
    path("api/products", api_views.latest_and_discount_product, name="product"),
    path('api/address/<int:id>/update/', api_views.update_address, name='api-update-address'),
    path('api/address/<int:id>/delete/', api_views.delete_address, name='api-delete-address'),
    path('api/address/set-active/', api_views.set_active_address, name='set-active-address'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
