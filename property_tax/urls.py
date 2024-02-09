from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import home, enumerate_property, view_properties, custom_logout, pay_tax, paystack_callback, payment_success, payment_failure, receipt_view, pay_tax_with_installments, payment_options, select_payment_option, payment_details, full_payment_form, process_payment, paystack_webhook, payment_confirmation
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('view-properties/', view_properties, name='view_properties'),
    path('', home, name='home'),
    path('enumerate/', login_required(enumerate_property), name='enumerate_property'),    
    path('pay-tax/', pay_tax, name='pay_tax'),
    path('pay-tax-with-installments/',pay_tax_with_installments, name='pay_tax_with_installments'),
    path('payment-success/paystack-callback/', paystack_callback, name='paystack_callback'),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', custom_logout, name='logout'),
    path('payment-options/', payment_options, name='payment_options'),
    path('select-payment-option/', select_payment_option, name='select_payment_option'),
    path('payment-details/', payment_details, name='payment_details'),
    path('payment-success/', payment_success, name='payment_success'),
    path('payment-failure/', payment_failure, name='payment_failure'),
    path('receipt/<int:property_id>/', receipt_view, name='receipt_view'),
    path('full-payment/<int:property_id>/', full_payment_form, name='full_payment_form'),
    path('process_payment/', process_payment, name='process_payment'),
    path('paystack/webhook/', paystack_webhook, name='paystack_webhook'),
    path('payment-confirmation/', payment_confirmation, name='payment_confirmation'),
]
    