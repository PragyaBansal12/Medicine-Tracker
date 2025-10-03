"""
URL configuration for crudapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),        # optional for admin
    path('', include('medicines.urls')),   # connects your medicines app
    path('accounts/', include('allauth.urls')),  # allauth urls
<<<<<<< HEAD
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
=======
    
]
>>>>>>> 83360a075e93833c40416f96463f397960494de8

