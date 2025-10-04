from django.urls import path
from . import views

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

    # Dashboard
    path('dashboard/', views.dashboard_view, name="dashboard"),
    path('dashboard/data/', views.dashboard_data, name="dashboard_data"),
    path('dashboard/log_dose/', views.log_dose, name='log_dose'),

    # Push subscription
    path('save-subscription/', views.save_subscription, name='save_subscription'),

    # Google Calendar OAuth
    path('google/calendar/connect/', views.google_calendar_auth, name='google_calendar_auth'),
    path('google/calendar/callback/', views.google_calendar_callback, name='google_calendar_callback'),
    path('calendar/add-event/<int:med_id>/', views.add_event, name='add_event'),
]
