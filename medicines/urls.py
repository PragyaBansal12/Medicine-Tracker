from django.urls import path
from . import views
from .views import save_subscription


urlpatterns = [
    # Auth
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # CRUD
    path('', views.medication_list, name='med_list'),
    path('add/', views.medication_create, name='med_add'),
    path('edit/<int:pk>/', views.medication_update, name='med_edit'),
    path('delete/<int:pk>/', views.medication_delete, name='med_delete'),

<<<<<<< HEAD
    # notifs
    path('get-vapid-public-key/', views.get_vapid_public_key, name='get_vapid_public_key'),
    path('save-subscription/', views.save_subscription, name='save_subscription'),
    

=======
    # Dashboard
    path('dashboard/', views.dashboard_view, name="dashboard"),
    path('dashboard/data/', views.dashboard_data, name="dashboard_data"),
    path('dashboard/log_dose/', views.log_dose, name='log_dose'),
>>>>>>> 83360a075e93833c40416f96463f397960494de8

]
