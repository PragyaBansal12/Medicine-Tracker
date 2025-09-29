from django.shortcuts import render, redirect, get_object_or_404
from .models import Medication

# READ (List)
def medication_list(request):
    meds = Medication.objects.all()  # show all medications
    return render(request, 'medicines/medication_list.html', {'meds': meds})

# CREATE
def medication_create(request):
    if request.method == 'POST':
        pill_name = request.POST['pill_name']
        dosage = request.POST['dosage']
        time = request.POST['time']
        frequency = request.POST['frequency']
        Medication.objects.create(
            pill_name=pill_name,
            dosage=dosage,
            time=time,
            frequency=frequency
        )
        return redirect('med_list')
    return render(request, 'medicines/medication_form.html')

# UPDATE
def medication_update(request, pk):
    med = get_object_or_404(Medication, pk=pk)
    if request.method == 'POST':
        med.pill_name = request.POST['pill_name']
        med.dosage = request.POST['dosage']
        med.time = request.POST['time']
        med.frequency = request.POST['frequency']
        med.save()
        return redirect('med_list')
    return render(request, 'medicines/medication_form.html', {'med': med})

# DELETE
def medication_delete(request, pk):
    med = get_object_or_404(Medication, pk=pk)
    med.delete()
    return redirect('med_list')
