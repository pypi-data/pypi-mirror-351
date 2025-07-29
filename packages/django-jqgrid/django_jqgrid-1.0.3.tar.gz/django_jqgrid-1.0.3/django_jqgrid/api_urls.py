"""
API URL Configuration for django_jqgrid
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django_jqgrid.api_views import JqGridModelViewSet, get_grid_config
from django_jqgrid.views import GridFilterViewSet

app_name = 'django_jqgrid_api'

# Router for filter management
filter_router = DefaultRouter()
filter_router.register(r'grid-filter', GridFilterViewSet, basename='gridfilter')

# Dynamic model routes
def get_model_urls():
    """Generate URL patterns for model CRUD operations"""
    return [
        path('<str:app_name>/<str:model_name>/', 
             JqGridModelViewSet.as_view({
                 'get': 'list',
                 'post': 'create'
             }), name='model-list'),
        
        path('<str:app_name>/<str:model_name>/<int:pk>/', 
             JqGridModelViewSet.as_view({
                 'get': 'retrieve',
                 'put': 'update',
                 'patch': 'partial_update',
                 'delete': 'destroy'
             }), name='model-detail'),
        
        path('<str:app_name>/<str:model_name>/bulk_action/', 
             JqGridModelViewSet.as_view({
                 'post': 'bulk_action'
             }), name='model-bulk-action'),
        
        path('<str:app_name>/<str:model_name>/export/', 
             JqGridModelViewSet.as_view({
                 'get': 'export'
             }), name='model-export'),
        
        path('<str:app_name>/<str:model_name>/import/', 
             JqGridModelViewSet.as_view({
                 'post': 'import_data'
             }), name='model-import'),
        
        path('<str:app_name>/<str:model_name>/config/', 
             get_grid_config, name='model-config'),
    ]

from .api_views import get_content_type_info

urlpatterns = [
    # Filter management endpoints
    path('django_jqgrid/', include(filter_router.urls)),
    
    # Content type info endpoint
    path('mainapp/content-type/', get_content_type_info, name='content-type-info'),
    
    # Model CRUD endpoints
    *get_model_urls(),
]