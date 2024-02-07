from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import home, enumerate_property, view_properties, custom_logout, pay_tax, paystack_callback, payment_success, payment_failure
from django.contrib.auth.views import LogoutView, LoginView

urlpatterns = [
    path('', home, name='home'),
    path('enumerate/', login_required(enumerate_property), name='enumerate_property'),
    path('view-properties/', view_properties, name='view_properties'),
    path('pay-tax/', pay_tax, name='pay_tax'),
    path('payment-success/paystack-callback/', paystack_callback, name='paystack_callback'),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', custom_logout, name='logout'),
    path('payment-success/', payment_success, name='payment_success'),
    path('payment-failure/', payment_failure, name='payment_failure'),
]
