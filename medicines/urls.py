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
]
