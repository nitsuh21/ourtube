from django.contrib import admin
from django.urls import path,include
from django.conf.urls import handler404

handler404 = 'accounts.views.error_404'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("home.urls")),
    path('accounts/',include('accounts.urls')),
    path('newsletter/',include('newsletter.urls')),
]
