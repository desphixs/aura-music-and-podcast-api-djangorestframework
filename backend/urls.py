"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
# We import include so we can link modular app url directories, and path to declare routes
from django.urls import include, path

# urlpatterns is the main master switchboard directory for the entire project.
# Every single URL that hits our server is checked against this list.
urlpatterns = [
    # Map the standard Django administrative panel
    path('admin/', admin.site.urls),
    
    # We include all URL endpoints from our 'accounts' app.
    # By prefixing this with 'api/auth/', every url defined inside 'accounts/urls.py'
    # will automatically be preceded by '/api/auth/'.
    # For example, our registration path becomes: 'api/auth/register/'
    path('api/auth/', include('accounts.urls')),
]
