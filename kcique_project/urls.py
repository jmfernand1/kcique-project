"""
URL configuration for kcique_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
# from django.views.generic import RedirectView # Ya no es necesario para la raíz
from automations import views as automations_views # Importar vistas de automations
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('automations/', include('automations.urls', namespace='automations')),
    path('', automations_views.home_view, name='home'),
    path('adagio/', include('adagio.urls')),
    path('dexter/', include('dexter.urls')),

    # Documentación de la API (OpenAPI 3 / drf-spectacular)
    # Esquema descargable en .yaml: /api/schema/
    # Esquema en .json:            /api/schema/?format=json
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # UI interactiva Swagger:      /api/docs/
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # UI alternativa ReDoc:        /api/redoc/
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
