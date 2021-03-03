from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # new
    path('oauth2/', include('oauth2_provider.urls')),
    path('api/', include('api.urls')),
    path('ussd/', include('ussd.urls')),
    path('', include('web.urls')),
]
