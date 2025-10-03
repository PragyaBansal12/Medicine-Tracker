from django.shortcuts import render, redirect, get_object_or_404
from .models import Medication, PushSubscription
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
import json

def signup_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken. Try login.")
            return redirect('signup')
        user = User.objects.create_user(username=username, password=password)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('med_list')
    return render(request, "medicines/signup.html")


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('med_list')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'medicines/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def medication_list(request):
    meds = Medication.objects.filter(user=request.user)

    meds_data = []
    for med in meds:
        times_list = med.times if isinstance(med.times, list) else [] 
        
        meds_data.append({
            "pill_name": med.pill_name,
            "dosage": med.dosage,
            "times": times_list,
            "frequency": med.frequency,
            "times_per_day": med.times_per_day
        })
    
    meds_data_json = json.dumps(meds_data, cls=DjangoJSONEncoder)

    return render(request, 'medicines/medication_list.html', {
        'meds': meds,
        "VAPID_PUBLIC_KEY": settings.VAPID_PUBLIC_KEY,
        "meds_data_json": meds_data_json
    })


@login_required
def medication_create(request):
    if request.method == "POST":
        pill_name = request.POST.get("pill_name")
        dosage = request.POST.get("dosage")
        frequency = request.POST.get("frequency_type")
        times_per_day = int(request.POST.get("times_per_day", 1))
        
        times = request.POST.getlist("times")

        if not pill_name or not dosage or not times:
            messages.error(request, "Please fill all required fields.")
            return redirect('med_add')

        Medication.objects.create(
            user=request.user,
            pill_name=pill_name,
            dosage=int(dosage),
            frequency=frequency,
            times_per_day=times_per_day,
            times=times
        )
        messages.success(request, f"{pill_name} added successfully!")
        return redirect('med_list')

    return render(request, "medicines/medication_form.html", {
        "med": None,
        "existing_times_json": json.dumps([])
    })


@login_required
def medication_update(request, pk):
    med = get_object_or_404(Medication, pk=pk, user=request.user)
    
    if request.method == 'POST':
        submitted_times = request.POST.getlist('times')
        
        med.pill_name = request.POST.get('pill_name')
        med.dosage = request.POST.get('dosage')
        med.frequency = request.POST.get('frequency_type')
        med.times = submitted_times
        med.times_per_day = len(submitted_times)
        
        if med.times_per_day == 0:
            messages.error(request, 'Error: At least one time is required.')
            return render(request, 'medicines/medication_form.html', {'med': med})

        try:
            med.save()
            messages.success(request, f"{med.pill_name} updated successfully!")
            return redirect('med_list')
        except Exception as e:
            print(f"Database Save Error: {e}")
            messages.error(request, f'Save failed due to a system error.')
            return render(request, 'medicines/medication_form.html', {'med': med})
    
    return render(request, 'medicines/medication_form.html', {'med': med})


@login_required
def medication_delete(request, pk):
    med = get_object_or_404(Medication, pk=pk, user=request.user)
    med.delete()
    messages.success(request, "Medication deleted successfully!")
    return redirect('med_list')


# In your views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def save_subscription(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            subscription = PushSubscription(
                user=request.user,  
                endpoint=data['endpoint'],
                p256dh=data['p256dh'],  
                auth=data['auth']
            )
            subscription.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            print(f"Error saving subscription: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error'})

@login_required
def get_vapid_public_key(request):
    """API endpoint to get VAPID public key"""
    return JsonResponse({
        'vapid_public_key': settings.VAPID_PUBLIC_KEY
    })