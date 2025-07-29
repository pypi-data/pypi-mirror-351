from django.urls import path, include
from django.views.generic import TemplateView

app_name = 'django_jqgrid'

urlpatterns = [
    # API endpoints
    path('api/', include('django_jqgrid.api_urls')),
    
    # Example page showcasing standalone grid
    path('example/', TemplateView.as_view(template_name='django_jqgrid/example_page.html'), name='jqgrid_example'),
]
