from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import PropertyForm, InstallmentPaymentForm
from .models import Property
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, HttpResponseServerError, Http404,HttpResponseBadRequest
import requests
import json
import uuid
import decimal
import logging
import paystack
from decimal import Decimal
from django.core.mail import send_mail
import traceback 
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.core.mail import send_mail
from django.template.loader import render_to_string, get_template
from django.template import TemplateDoesNotExist
from django.db import transaction




logger = logging.getLogger(__name__)

# Load Paystack secret key from settings
paystack_secret_key = settings.PAYSTACK_SECRET_KEY
paystack_public_key = settings.PAYSTACK_PUBLIC_KEY


def home(request):
    return render(request, 'property_tax/index.html')


@login_required
def enumerate_property(request):
    if request.method == 'POST':
        print("POST request received")
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            print("Form is valid")
            property_instance = form.save(commit=False)
            property_instance.calculate_tax()
            property_instance.save()

            messages.success(request, f'Property enumerated successfully! Tax Payable: &#8358;{property_instance.tax_payable:.4f}')
            return redirect('enumerate_property')
        else:
            print("Form is invalid")
            messages.error(request, 'Error in form submission. Please check the form and try again.')
    else:
        print("GET request received")
        form = PropertyForm()

    properties = Property.objects.all()
    return render(request, 'property_tax/enumerate.html', {'form': form, 'properties': properties})


def view_properties(request):
    properties = Property.objects.all()
    return render(request, 'property_tax/view_properties.html', {'properties': properties})

def select_payment_option(request):
    if request.method == 'POST':
        property_id = request.POST.get('property_id')
        print(property_id)
    return render(request, 'property_tax/select_payment_option.html', {'property': property})

def custom_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return render(request, 'registration/logout.html')


def process_payment(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        email = request.POST.get('email')
        paystack_secret_key = settings.PAYSTACK_SECRET_KEY
        
        payload = {
            'email': email,
            'amount': int(amount) * 100,
            'callback_url': reverse('paystack_callback'),
            # Add more metadata if needed
        }

        headers = {
            'Authorization': f'Bearer {paystack_secret_key}',
            'Content-Type': 'application/json',
        }

        try:
            response = requests.post('https://api.paystack.co/transaction/initialize', data=json.dumps(payload), headers=headers)
            data = response.json()
            if response.status_code == 200 and data.get('status'):
                payment_url = data.get('data').get('authorization_url')
                return JsonResponse({'payment_url': payment_url})
            else:
                error_message = f'Failed to initialize transaction: {data.get("message")}'
                return JsonResponse({'error': error_message}, status=400)
        except Exception as e:
            error_message = f'An unexpected error occurred: {str(e)}'
            logger.error(error_message)
            return JsonResponse({'error': error_message}, status=500)

    else:
        return JsonResponse({'error': 'This endpoint only supports POST requests for payment processing.'})



def payment_success(request):
    reference = request.GET.get('reference')
    paystack_secret_key = settings.PAYSTACK_SECRET_KEY

    verify_url = f'https://api.paystack.co/transaction/verify/{reference}'
    headers = {'Authorization': f'Bearer {paystack_secret_key}'}

    try:
        verify_response = requests.get(verify_url, headers=headers)
        verify_data = verify_response.json()

        if verify_response.status_code == 200 and verify_data.get('status') == 'success':
            # Payment successful, get metadata details
            metadata = verify_data.get('data', {}).get('metadata', {})
            return render(request, 'property_tax/payment_success.html', {'metadata': metadata})
        else:
            logger.error(f'Failed to verify payment. Response: {verify_data}')
            return JsonResponse({'status': 'failure'})
    except Exception as e:
        error_message = f'An unexpected error occurred during payment verification: {str(e)}'
        logger.error(error_message)
        return JsonResponse({'error': error_message}, status=500)
    

def payment_details(request):
    selected_property_id = request.POST.get('selected_property_id')
    payment_option = request.POST.get('payment_option')

    property = get_object_or_404(Property, pk=selected_property_id)

    return render(request, 'property_tax/payment_details.html', {'property': property, 'payment_option': payment_option})


def pay_tax_with_installments(request):
    template = get_template('property_tax/pay_tax_with_installments.html')
    print(template.origin)
    try:
        return render(request, 'property_tax/pay_tax_with_installments.html')
    except TemplateDoesNotExist:
        return HttpResponseServerError("Template file 'property_tax/pay_tax_with_installments.html' not found.")


def payment_failure(request):
    return render(request, 'property_tax/payment_failure.html')

def receipt_view(request, property_id):
    # Retrieve the property object using the property_id
    property_obj = get_object_or_404(Property, pk=property_id)

    # Render the receipt template and pass the property object
    return render(request, 'property_tax/receipt.html', {'property': property_obj})



@transaction.atomic
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
            
            # Call calculate_tax method to ensure tax_payable is calculated
            selected_property.calculate_tax()
            
            amount_paid = selected_property.tax_payable  # amount_paid as Decimal
            
            email = 'ezebo001@gmail.com'
            
            payload = {
                'email': email,
                'amount': int(amount_paid * 100),  # Convert amount to kobo
                'key': settings.PAYSTACK_PUBLIC_KEY,
                'currency': 'NGN',
                'reference': generate_transaction_reference(),  # Generate unique reference
                'callback_url': request.build_absolute_uri(reverse('paystack_callback')),
            }
            response = requests.post('https://api.paystack.co/transaction/initialize', json=payload,
                                     headers={'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}', 'Content-Type': 'application/json'})

            if response.status_code == 200:
                data = response.json()
                authorization_url = data.get('data').get('authorization_url')
                # Deduct the amount paid from the tax payable
                selected_property.tax_payable -= amount_paid
                selected_property.save()
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



def paystack_webhook(request):
    # Log the received payload
    logger.info("Received webhook payload: %s", request.body)

    try:
        # Parse the webhook payload
        payload = json.loads(request.body)
        
        # Extract relevant information from the payload
        event = payload.get('event')
        data = payload.get('data')

        # Check if it's a successful payment event
        if event == 'charge.success' and data:
            # Extract payment details
            payment_reference = data.get('reference')
            amount_paid = data.get('amount')

            # Log the payment reference
            logger.info("Payment Reference: %s", payment_reference)

            # Retrieve the corresponding tax record based on the payment reference
            # Update the 'tax payable' column for the tax record
            # Example: 
            # tax_record = Tax.objects.get(payment_reference=payment_reference)
            # tax_record.tax_payable += amount_paid
            # tax_record.save()
            # Log the payment details or perform any additional processing

            # Return a success response to Paystack
            return HttpResponse(status=200)
        else:
            # Log the event if it's not a successful payment event
            logger.info("Non-payment event received: %s", event)

            # Return a failure response or ignore the event
            return HttpResponse(status=400)
    except Exception as e:
        # Log any exceptions that occur during processing
        logger.error("Error processing webhook: %s", e)
        return HttpResponse(status=500)
    


@csrf_exempt
def paystack_callback(request):
    if request.method == 'POST':
        reference = request.POST.get('reference')
        paystack_secret_key = settings.PAYSTACK_SECRET_KEY

        if not reference:
            return HttpResponseBadRequest('Missing transaction reference')

        verify_url = f'https://api.paystack.co/transaction/verify/{reference}'
        headers = {'Authorization': f'Bearer {paystack_secret_key}'}

        try:
            # Log the transaction reference
            logger.info(f"Verifying payment for transaction reference: {reference}")

            verify_response = requests.get(verify_url, headers=headers)
            verify_data = verify_response.json()

            if verify_response.status_code == 200:
                if verify_data.get('status') == False:
                    # Payment verification failed
                    message = verify_data.get('message', 'Unknown error')
                    logger.error(f"Failed to verify payment. Response: {verify_data}")
                    if verify_data.get('code') == 'transaction_not_found':
                        # Log the specific error when transaction reference is not found
                        logger.error('Transaction reference not found')
                    return JsonResponse({'status': 'failure', 'message': message})
                else:
                    # Payment successful, update your database or perform other actions
                    metadata = verify_data.get('data', {}).get('metadata', {})
                    logger.info(f"Payment successful. Metadata: {metadata}")
                    return JsonResponse({'status': 'success'})
            else:
                # Unexpected response from Paystack API
                logger.error(f"Unexpected response from Paystack API: {verify_response.text}")
                return JsonResponse({'status': 'failure', 'message': 'Failed to verify payment'})

        except Exception as e:
            error_message = f'An unexpected error occurred during payment verification: {str(e)}'
            logger.error(error_message)
            return JsonResponse({'status': 'failure', 'error': error_message}, status=500)

    elif request.method == 'GET':
        # Handle GET request (acknowledge receipt)
        # You can redirect to a success page or render a success message
        return HttpResponseRedirect('/payment-success/')

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    


def payment_confirmation(request):
    # Retrieve payment details from Paystack redirect URL parameters
    payment_reference = request.GET.get('reference')
    amount_paid = request.GET.get('amount')

    if amount_paid is not None:
        # Convert amount_paid to Decimal
        amount_paid_decimal = Decimal(amount_paid)

        # Update tax payable column based on payment reference
        try:
            property_record = Property.objects.get(payment_reference=payment_reference)
            property_record.tax_payable += amount_paid_decimal
            property_record.save()
            confirmation_message = "Payment successful. Tax payable updated."
        except Property.DoesNotExist:
            confirmation_message = "Error: Property record not found for payment reference."
    else:
        confirmation_message = "Error: Amount paid is None."

    return render(request, 'property_tax/confirmation_page.html', {'confirmation_message': confirmation_message})


def generate_transaction_reference():
    # Generate a UUID (Universally Unique Identifier) as the transaction reference
    return str(uuid.uuid4().hex)


def payment_options(request):
    if request.method == 'POST':
        # Handle form submission for payment option
        # Check if the user selected full payment or installment payment
        payment_option = request.POST.get('payment_option')
        if payment_option == 'full_amount':
            # Redirect to Paystack checkout for full payment
            # Replace this with your Paystack checkout logic
            return HttpResponseRedirect('/paystack_checkout_full_amount/')
        elif payment_option == 'installments':
            # Redirect to installment payment form
            return HttpResponseRedirect('/paystack_checkout_installments/')
    else:
        # Render the payment options page
        return render(request, 'property_tax/payment_options.html')


def full_payment_form(request, property_id):
    try:
        # Check if property_id is not None
        if property_id is None:
            raise Http404("Property ID is missing")

        # Check if property_id is a valid integer
        if not isinstance(property_id, int):
            raise Http404("Invalid property ID")

        # Fetch the property object using the property_id
        property_obj = get_object_or_404(Property, pk=property_id)

        if request.method == 'POST':
            # Process the form data and redirect to Paystack
            # Example: Save the form data to the database and then redirect to Paystack
            return render(request, 'paystack_payment.html')  # Example: Rendering Paystack payment page
        else:
            # Render the full payment form template with the property data
            return render(request, 'property_tax/full_payment_form.html', {'property': property_obj, 'property_id': property_id})
    except Exception as e:
        # Log the exception
        logger.error(f"Error processing full payment form for property ID {property_id}: {e}")
        # Return a 404 error page
        raise Http404("Page not found")
        

def pay_tax_with_installments(request):
    if request.method == 'POST':
        form = InstallmentPaymentForm(request.POST)
        if form.is_valid():
            # Process installment payment form data
            # Implement your logic here
            return redirect('payment_success')  # Redirect to payment success page after processing
    else:
        form = InstallmentPaymentForm()
    
    return render(request, 'property_tax/pay_tax_with_installments.html', {'form': form})


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
