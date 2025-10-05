from django.shortcuts import render, redirect, get_object_or_404
from .models import Medication, PushSubscription, DoseLog
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
import json
from datetime import date, datetime, timedelta
from django.utils import timezone

# SIGNUP
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
        if user:
            login(request, user)
            return redirect('med_list')
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

    return render(request, "medicines/medication_form.html", {"med": None})


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
        
        # Basic validation check
        if med.times_per_day == 0:
            messages.error(request, 'At least one time is required.')
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

# DELETE
@login_required
def medication_delete(request, pk):
    med = get_object_or_404(Medication, pk=pk, user=request.user)
    med.delete()
    messages.success(request, "Medication deleted successfully!")
    return redirect('med_list')

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

# ===========================
# DASHBOARD VIEW
# ===========================
@login_required
def dashboard_view(request):
    meds = Medication.objects.filter(user=request.user)
    today = date.today()
    now = timezone.now()

    dose_data = []
    for med in meds:
        for t_str in med.times:
            t_obj = datetime.strptime(t_str, "%H:%M").time()
            scheduled_dt = timezone.make_aware(datetime.combine(today, t_obj))
            
            # ALWAYS create DoseLog entry to ensure we have an ID
            dose_log, created = DoseLog.objects.get_or_create(
                user=request.user,
                medication=med,
                scheduled_time=scheduled_dt,
                defaults={'status': 'pending'}
            )
            
            # Auto-mark as missed if time has passed and still pending
            if dose_log.status == 'pending' and scheduled_dt < now:
                dose_log.status = 'missed'
                dose_log.save()
            
            dose_data.append({
                'med_id': med.id,
                'pill_name': med.pill_name,
                'time': t_str,
                'status': dose_log.status,
                'dose_log_id': dose_log.id  # This will always have a value now
            })

    # Calculate adherence
    total_doses = len(dose_data)
    taken_doses = sum(1 for d in dose_data if d['status'] == 'taken')
    missed_doses = sum(1 for d in dose_data if d['status'] == 'missed')
    adherence = round((taken_doses / total_doses) * 100, 1) if total_doses else 0

    # Calculate streak
    streak = 0
    for i in range(30):
        day = today - timedelta(days=i)
        day_start = timezone.make_aware(datetime.combine(day, datetime.min.time()))
        day_end = timezone.make_aware(datetime.combine(day, datetime.max.time()))
        day_logs = DoseLog.objects.filter(
            user=request.user, 
            scheduled_time__range=(day_start, day_end)
        )
        
        expected_doses_count = sum(len(med.times) for med in meds)
        taken_doses_count = day_logs.filter(status='taken').count()
        
        if expected_doses_count > 0 and taken_doses_count == expected_doses_count:
            streak += 1
        else:
            break

    # Next dose
    next_dose_time = "--:--"
    for d in sorted(dose_data, key=lambda x: x['time']):
        dose_time_obj = datetime.strptime(d['time'], "%H:%M").time()
        scheduled_dt = timezone.make_aware(datetime.combine(today, dose_time_obj))
        if scheduled_dt > now and d['status'] == 'pending':
            next_dose_time = d['time']
            break

    # Weekly adherence data
    weekly_adherence = []
    week_days = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        week_days.append(day.strftime('%a'))
        
        day_start = timezone.make_aware(datetime.combine(day, datetime.min.time()))
        day_end = timezone.make_aware(datetime.combine(day, datetime.max.time()))
        
        day_logs = DoseLog.objects.filter(
            user=request.user, 
            scheduled_time__range=(day_start, day_end)
        )
        
        expected_doses = sum(len(med.times) for med in meds)
        taken_doses = day_logs.filter(status='taken').count()
        
        day_adherence = round((taken_doses / expected_doses) * 100, 1) if expected_doses > 0 else 0
        weekly_adherence.append(day_adherence)

    context = {
        'meds': meds,
        'dose_data': dose_data,
        'dose_data_json': json.dumps(dose_data),
        'adherence': adherence,
        'streak': streak,
        'next_dose': next_dose_time,
        'total_doses': total_doses,
        'taken_doses': taken_doses,
        'missed_doses': missed_doses,
        'weekly_adherence_json': json.dumps(weekly_adherence),
        'week_days_json': json.dumps(week_days),
    }
    return render(request, "medicines/dashboard.html", context)

# ===========================
# TOGGLE DOSE STATUS
# ===========================
@login_required
@csrf_exempt
def toggle_dose_status(request):
    """Simple toggle between taken/missed"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            dose_log_id = data.get('dose_log_id')
            new_status = data.get('status')  # 'taken' or 'missed'
            
            # Safety check - ensure dose_log_id is valid
            if not dose_log_id:
                return JsonResponse({'status': 'error', 'message': 'Missing dose log ID'})
            
            try:
                dose_log_id = int(dose_log_id)  # Convert to integer
            except (ValueError, TypeError):
                return JsonResponse({'status': 'error', 'message': 'Invalid dose log ID'})
            
            dose_log = DoseLog.objects.get(id=dose_log_id, user=request.user)
            
            # Update status
            dose_log.status = new_status
            if new_status == 'taken':
                dose_log.timestamp = timezone.now()
            
            dose_log.save()
            
            return JsonResponse({
                'status': 'success',
                'new_status': dose_log.status
            })
            
        except DoseLog.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Dose not found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid method'})

# ===========================
# DASHBOARD DATA (AJAX)
# ===========================
@login_required
def dashboard_data(request):
    meds = Medication.objects.filter(user=request.user)
    today = date.today()

    dose_data = []
    for med in meds:
        for t_str in med.times:
            t_obj = datetime.strptime(t_str, "%H:%M").time()
            scheduled_dt = timezone.make_aware(datetime.combine(today, t_obj))
            try:
                log = DoseLog.objects.get(user=request.user, medication=med, scheduled_time=scheduled_dt)
                status = log.status
            except DoseLog.DoesNotExist:
                status = 'pending'
            dose_data.append({
                'med_id': med.id,
                'pill_name': med.pill_name,
                'time': t_str,
                'status': status
            })

    taken_count = sum(1 for d in dose_data if d['status'] == 'taken')
    missed_count = sum(1 for d in dose_data if d['status'] == 'missed')
    pending_count = sum(1 for d in dose_data if d['status'] == 'pending')

    return JsonResponse({
        'dose_data': dose_data,
        'taken_count': taken_count,
        'missed_count': missed_count,
        'pending_count': pending_count,
        'total_doses': len(dose_data)
    })


# ===========================
# DOSE LOG AJAX (For dashboard buttons)
# ===========================
@login_required
@csrf_exempt
def log_dose(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            med = Medication.objects.get(id=data['med_id'], user=request.user)
            dose_time = datetime.strptime(data['time'], "%H:%M").time()
            scheduled_dt = timezone.make_aware(datetime.combine(date.today(), dose_time))
            status = 'taken' if data.get('taken', True) else 'missed'

            DoseLog.objects.update_or_create(
                user=request.user,
                medication=med,
                scheduled_time=scheduled_dt,
                defaults={'status': status}
            )
            return JsonResponse({'status': 'success', 'message': 'Dose logged successfully'})
        except Medication.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Medication not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


# ===========================
# MARK DOSE TAKEN (For push notification action)
# ===========================
@login_required
@csrf_exempt
def mark_dose_taken(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            dose_log = DoseLog.objects.get(
                id=data['dose_log_id'],
                user=request.user  # Security: ensure user owns this dose log
            )
            dose_log.status = 'taken'
            dose_log.timestamp = timezone.now()  # Update timestamp to when taken
            dose_log.save()
            
            return JsonResponse({
                'status': 'success', 
                'message': f'{dose_log.medication.pill_name} marked as taken'
            })
            
        except DoseLog.DoesNotExist:
            return JsonResponse({
                'status': 'error', 
                'message': 'Dose log not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'status': 'error', 
        'message': 'Invalid request method'
    }, status=405)


# ===========================
# GET TODAY'S DOSE LOGS
# ===========================
@login_required
def get_today_dose_logs(request):
    today = date.today()
    today_start = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    today_end = timezone.make_aware(datetime.combine(today, datetime.max.time()))
    
    dose_logs = DoseLog.objects.filter(
        user=request.user,
        scheduled_time__range=(today_start, today_end)
    ).select_related('medication')
    
    logs_data = []
    for log in dose_logs:
        logs_data.append({
            'id': log.id,
            'medication_name': log.medication.pill_name,
            'scheduled_time': log.scheduled_time.strftime('%H:%M'),
            'status': log.status,
            'taken_time': log.timestamp.strftime('%H:%M') if log.status == 'taken' else None
        })
    
    return JsonResponse({'dose_logs': logs_data})