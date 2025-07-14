from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse, HttpResponse
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.conf import settings
from .models import Download
import requests
import json
import uuid
import os

from .models import Ebook, Payment
from .forms import EbookUploadForm


@login_required
def initiate_payment(request, pk):
    ebook = get_object_or_404(Ebook, pk=pk)
    reference = str(uuid.uuid4())
    callback_url = request.build_absolute_uri('/verify-payment/')

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "email": request.user.email,
        "amount": int(ebook.price * 100),  # Kobo
        "reference": reference,
        "callback_url": callback_url,
    }

    # Save payment record in database
    Payment.objects.create(
        user=request.user,
        ebook=ebook,
        amount=ebook.price,
        reference=reference
    )

    response = requests.post('https://api.paystack.co/transaction/initialize', json=data, headers=headers, timeout=10)
    res_data = response.json()

    if res_data.get("status"):
        return redirect(res_data["data"]["authorization_url"])
    else:
        return HttpResponse("Payment initialization failed", status=400)

def ebook_list(request):
    query = request.GET.get('q')
    genre = request.GET.get('genre')
    max_price = request.GET.get('max_price')

    ebooks = Ebook.objects.all()

    if query:
        ebooks = ebooks.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )
    if genre:
        ebooks = ebooks.filter(genre__iexact=genre)
    if max_price:
        ebooks = ebooks.filter(price__lte=max_price)

    return render(request, 'library/ebook_list.html', {'ebooks': ebooks})


def sign_up(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
        return render(request, 'library/sign_up.html', {'form': form})
    


from django.http import HttpResponseForbidden

@login_required
def download_ebook(request, pk):
    ebook = get_object_or_404(Ebook, pk=pk)

    has_paid = Payment.objects.filter(user=request.user, ebook=ebook, verified=True).exists()

    if not has_paid:
        return HttpResponseForbidden("You are not allowed to download this ebook.")

    ebook.download_count += 1
    ebook.save()

    file_path = ebook.file.path
    try:
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    except FileNotFoundError:
        return HttpResponse("File not found.", status=404)


@login_required
def dashboard(request):
    paid_ebooks = Payment.objects.filter(user=request.user, verified=True).select_related('ebook')
    downloads = Download.objects.filter(user=request.user).select_related('ebook').order_by('-timestamp')

    return render(request, 'library/dashboard.html', {
        'paid_ebooks': paid_ebooks,
        'user': request.user
    })

def custom_logout(request):
    logout(request)
    return redirect('/')



@staff_member_required
def upload_ebook(request):
    if request.method == 'POST':
        form = EbookUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('ebook_list')
    else:
        form = EbookUploadForm()
    return render(request, 'library/upload_ebook.html', {'form': form})

def sales_report(request):
    payments = Payment.objects.filter(verified=True).select_related('ebook', 'user')
    return render(request, 'library/sales_report.html', {'payments': payments})


@login_required
def verify_payment(request):
    reference = request.GET.get('reference')
    
    if not reference:
        return HttpResponse("No payment reference provided", status=400)

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }

    try:
        response = requests.get(f'https://api.paystack.co/transaction/verify/{reference}', headers=headers)
        res_data = response.json()
    except Exception as e:
        return HttpResponse("Error connecting to Paystack", status=500)

    if not res_data.get('status') or 'data' not in res_data:
        return HttpResponse("Invalid response from Paystack", status=400)

    try:
        payment = Payment.objects.get(reference=reference)

        if payment.verified:
            return redirect('dashboard')  # already verified

        if res_data['data']['status'] == 'success':
            payment.verified = True
            payment.save()

    except Payment.DoesNotExist:
        return HttpResponse("Invalid payment reference", status=404)

    return redirect('dashboard')



@login_required
def ebook_detail(request, pk):
    ebook = get_object_or_404(Ebook, pk=pk)

    has_paid = Payment.objects.filter(user=request.user, ebook=ebook, verified=True).exists()

    return render(request, 'library/ebook_detail.html', {
        'ebook': ebook,
        'has_paid': has_paid,
    })
