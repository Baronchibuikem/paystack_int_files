from django.db import transaction
from django.shortcuts import render,redirect
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.core.signing import BadSignature, SignatureExpired, dumps as signing_encode, loads as signing_decode
from django.utils import timezone
from django.contrib import messages

from app_payment import models as app_payment_models
from libs import paystack_api

#@login_required
def payment_plans(request):
    if request.method == 'POST':
        selected_plan = request.POST["name-select-plan"]

        #tokenize plan
        plan_tokenized = signing_encode(
            selected_plan,
            salt=settings.SECRET_KEY
        )

        return redirect(
            reverse(
                'app_payment:pay',
                args=[plan_tokenized]
            )
        )
    
    if request.method == 'GET':
        plans = []
        plans = app_payment_models.Plan.objects.all()

        context = {
            "plans":plans
        }
        return render(request, 'app_payment/payment_plans.html', context=context)

#@login_required
#@transaction.atomic
@csrf_protect
def pay(request,plan_name_tokenized):

    context = {}

    plan_name = ""

    try:
        plan_name = signing_decode(
            plan_name_tokenized,
            salt=settings.SECRET_KEY,
            max_age=timezone.timedelta(days=1)
        )

        plan_obj = app_payment_models.Plan.objects.get(name=plan_name)

        paystack = paystack_api.PaystackAccount(
            settings.PAYSTACK_EMAIL,
            settings.PAYSTACK_PUBLIC_KEY,
            plan_obj.price
        )

        context = {
            'currency': settings.PAYMENT_CURRENCY,
            'plan': plan_obj,
            'paystack': paystack,
            'paypal_client_id': settings.PAYPAL_CLIENT_ID,
            'plan_name_tokenized': plan_name_tokenized
        }

        #FOR PAYSTACK TRANSACTION COMPLETED
        if request.method == 'POST':
            #check for the hidden-field paystack inserts in the page's form action
            if paystack.verify_transaction(request.POST['reference']):
                
                messages.success(request,"paystack payment successfull")

                #update user subscriptions

        #FOR PAYPAL TRANSACTION COMPLETED
        if request.method == 'GET':
            #check for the query-param
            if request.GET.get("paypal_success","false") == "true":

                messages.success(request,"paypal payment successfull")

                #update user subscriptions

    except (BadSignature, SignatureExpired):
        context = {}

    return render(request, 'app_payment/pay.html', context=context)