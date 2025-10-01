from django.shortcuts import render, redirect, get_object_or_404
from .models import Medication
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages

# SIGNUP
def signup_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken. Try login.")
            return redirect('signup')
        user = User.objects.create_user(username=username, password=password)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')  # auto login after signup
        return redirect('med_list')
    return render(request, "medicines/signup.html")

# LOGIN
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('med_list')  # redirect after login
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'medicines/login.html')

# LOGOUT
def logout_view(request):
    logout(request)
    return redirect('login')

# READ (List)
@login_required
def medication_list(request):
    meds = Medication.objects.filter(user=request.user)  # only logged-in user's meds
    return render(request, 'medicines/medication_list.html', {'meds': meds})

# CREATE / ADD MEDICATION
@login_required
def medication_create(request):
    if request.method == "POST":
        pill_name = request.POST.get("pill_name")
        dosage = request.POST.get("dosage")
        frequency = request.POST.get("frequency_type")
        times_per_day = int(request.POST.get("times_per_day", 1))
        
        # Get all times as a list
        times = request.POST.getlist("times")

        if not pill_name or not dosage or not times:
            messages.error(request, "Please fill all required fields.")
            return redirect('med_add')

        # Save medication
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

    # GET request
    return render(request, "medicines/medication_form.html", {"med": None})


# UPDATE
@login_required
def medication_update(request, pk):  
    med = get_object_or_404(Medication, pk=pk, user=request.user)
    
    if request.method == 'POST':
        submitted_times = request.POST.getlist('times') 
        
        # Update standard fields
        med.pill_name = request.POST.get('pill_name')
        med.dosage = request.POST.get('dosage')
        med.frequency = request.POST.get('frequency_type') 
        med.times = submitted_times
        med.times_per_day = len(submitted_times) 
        
        # Basic validation check
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

# DELETE
@login_required
def medication_delete(request, pk):
    med = get_object_or_404(Medication, pk=pk, user=request.user)  # ensure user owns it
    med.delete()
    return redirect('med_list')
