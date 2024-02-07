from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import PropertyForm, PaymentForm
from .models import Property
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
import requests
import json
import logging
from django.core.mail import send_mail
import traceback 
from django.shortcuts import get_object_or_404
from django.template import RequestContext



logger = logging.getLogger(__name__)

# Load Paystack secret key from settings
paystack_secret_key = settings.PAYSTACK_SECRET_KEY
paystack_public_key = settings.PAYSTACK_PUBLIC_KEY


def home(request):
    return render(request, 'property_tax/index.html')


@login_required
def enumerate_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property_instance = form.save(commit=False)
            property_instance.calculate_tax()
            property_instance.save()

            messages.success(request, f'Property enumerated successfully! Tax Payable: &#8358;{property_instance.tax_payable:.4f}')
            return redirect('enumerate_property')
        else:
            messages.error(request, 'Error in form submission. Please check the form and try again.')
    else:
        form = PropertyForm()

    properties = Property.objects.all()
    return render(request, 'property_tax/enumerate.html', {'form': form, 'properties': properties})


def view_properties(request):
    properties = Property.objects.all()
    return render(request, 'property_tax/view_properties.html', {'properties': properties})


def custom_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return render(request, 'registration/logout.html')


def payment_success(request):
    return render(request, 'property_tax/payment_success.html')


def payment_failure(request):
    return render(request, 'property_tax/payment_failure.html')







# views.py
def pay_tax(request):
    if request.method == 'GET':
        properties = Property.objects.all()
        return render(request, 'property_tax/pay_tax.html', {'properties': properties})
    
    elif request.method == 'POST':
        print(request.POST)
        property_id = request.POST.get('selectedRow')
        
        try:
            if not property_id:
                error_message = 'Property ID is required.'
                messages.error(request, error_message)
                print(error_message)
                return render(request, 'property_tax/pay_tax.html', {'error_message': error_message})
            
            selected_property = get_object_or_404(Property, pk=property_id)
            amount = selected_property.tax_payable * 100
            
            email = 'ezebo001@gmail.com'
            
            payload = {
                'email': email,
                'amount': int(amount),
                'key': settings.PAYSTACK_PUBLIC_KEY,
                'currency': 'NGN',
                'callback': reverse('paystack_callback'),
            }
            response = requests.post('https://api.paystack.co/transaction/initialize', data=json.dumps(payload),
                                     headers={'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}', 'Content-Type': 'application/json'})

            if response.status_code == 200:
                data = response.json()
                authorization_url = data.get('data').get('authorization_url')
                return redirect(authorization_url)
            else:
                error_message = f'Failed to initialize transaction: {response.text}'
                messages.error(request, error_message)
                print(error_message)
                return render(request, 'property_tax/pay_tax.html', {'error_message': error_message})
        
        except Property.DoesNotExist:
            error_message = 'Property with the provided ID does not exist.'
            messages.error(request, error_message)
            print(error_message)
            return render(request, 'property_tax/pay_tax.html', {'error_message': error_message})
        
        except Exception as e:
            error_message = f'An unexpected error occurred: {str(e)}'
            messages.error(request, error_message)
            print(error_message)
            traceback.print_exc()
            return render(request, 'property_tax/pay_tax.html', {'error_message': error_message})
    
    else:
        error_message = 'Method not allowed'
        messages.error(request, error_message)
        print(error_message)
        return render(request, 'error.html', {'message': error_message})



@csrf_exempt
def paystack_callback(request):
    if request.method == 'POST':
        # Handle POST request
        reference = request.POST.get('reference')

        # Verify transaction
        verify_url = f'https://api.paystack.co/transaction/verify/{reference}'
        verify_response = requests.get(verify_url, headers={'Authorization': f'Bearer {paystack_secret_key}'})

        if verify_response.status_code == 200:
            verify_data = verify_response.json()
            if verify_data.get('status') == 'success':
                # Payment successful
                return JsonResponse({'status': 'success'})
            else:
                # Payment failed
                return JsonResponse({'status': 'failure'})
        else:
            # Error in verifying transaction
            return JsonResponse({'error': 'Failed to verify transaction'}, status=500)
    elif request.method == 'GET':
        # Handle GET request (acknowledge receipt)
        # Redirect to payment success page
        return redirect('payment_success')
    else:
        # Return error response for other request methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)



@csrf_exempt
def payment_verification(request):
    if request.method == 'POST':
        payload = request.body
        headers = {
            'Authorization': f'Bearer {paystack_secret_key}',
            'Content-Type': 'application/json',
        }
        response = requests.post('https://api.paystack.co/transaction/verify', data=payload, headers=headers)
        # Process response and update payment status in your database
        return HttpResponse(status=200)
    return HttpResponse(status=400)
