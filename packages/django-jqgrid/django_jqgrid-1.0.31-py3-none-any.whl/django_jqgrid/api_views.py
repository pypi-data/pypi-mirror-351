"""
API Views for django_jqgrid
Provides generic ViewSets for handling jqGrid data operations
"""
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer
import json

from .mixins import JqGridConfigMixin, JqGridBulkActionMixin
from .pagination import JqGridPagination
from .filters import JqGridFilterBackend
# JqGridSerializer not needed - using dynamic serializers


class JqGridModelViewSet(JqGridConfigMixin, JqGridBulkActionMixin, viewsets.ModelViewSet):
    """
    Generic ViewSet for jqGrid operations
    Dynamically handles any model based on URL parameters
    """
    permission_classes = []  # Temporarily disabled for testing
    pagination_class = JqGridPagination
    filter_backends = [JqGridFilterBackend]
    
    def get_model(self):
        """Get model class from URL parameters"""
        app_name = self.kwargs.get('app_name')
        model_name = self.kwargs.get('model_name')
        
        try:
            return apps.get_model(app_name, model_name)
        except LookupError:
            return None
    
    def get_queryset(self):
        """Get queryset for the model"""
        model = self.get_model()
        if not model:
            from django.db.models import QuerySet
            return QuerySet().none()
        
        queryset = model.objects.all()
        
        # Apply select_related and prefetch_related for optimization
        for field in model._meta.fields:
            if field.many_to_one or field.one_to_one:
                queryset = queryset.select_related(field.name)
        
        for field in model._meta.many_to_many:
            queryset = queryset.prefetch_related(field.name)
        
        return queryset
    
    def get_serializer_class(self):
        """Dynamically create serializer for the model"""
        model = self.get_model()
        if not model:
            return ModelSerializer
        
        # Check if model has custom serializer
        serializer_name = f"{model.__name__}Serializer"
        app_module = apps.get_app_config(model._meta.app_label).module
        
        # Try to import custom serializer
        try:
            serializers_module = __import__(f"{app_module.__name__}.serializers", fromlist=[serializer_name])
            if hasattr(serializers_module, serializer_name):
                return getattr(serializers_module, serializer_name)
        except (ImportError, AttributeError):
            pass
        
        # Create dynamic serializer
        # Store model in a variable that can be accessed in the Meta class
        _model = model
        
        class DynamicModelSerializer(ModelSerializer):
            class Meta:
                model = _model
                fields = '__all__'
        
        return DynamicModelSerializer
    
    def list(self, request, *args, **kwargs):
        """Override list to format response for jqGrid"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Handle jqGrid search
        if request.GET.get('_search') == 'true':
            queryset = self.apply_jqgrid_filters(queryset, request)
        
        # Handle sorting
        sidx = request.GET.get('sidx', 'id')
        sord = request.GET.get('sord', 'asc')
        if sidx:
            order_by = f"{'-' if sord == 'desc' else ''}{sidx}"
            queryset = queryset.order_by(order_by)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def apply_jqgrid_filters(self, queryset, request):
        """Apply jqGrid search filters"""
        filters = request.GET.get('filters')
        if filters:
            try:
                filters_dict = json.loads(filters)
                group_op = filters_dict.get('groupOp', 'AND')
                rules = filters_dict.get('rules', [])
                
                q_objects = []
                for rule in rules:
                    field = rule['field']
                    op = rule['op']
                    data = rule['data']
                    
                    # Build query based on operation
                    if op == 'eq':
                        q_objects.append(Q(**{field: data}))
                    elif op == 'ne':
                        q_objects.append(~Q(**{field: data}))
                    elif op == 'lt':
                        q_objects.append(Q(**{f"{field}__lt": data}))
                    elif op == 'le':
                        q_objects.append(Q(**{f"{field}__lte": data}))
                    elif op == 'gt':
                        q_objects.append(Q(**{f"{field}__gt": data}))
                    elif op == 'ge':
                        q_objects.append(Q(**{f"{field}__gte": data}))
                    elif op == 'cn':  # contains
                        q_objects.append(Q(**{f"{field}__icontains": data}))
                    elif op == 'nc':  # not contains
                        q_objects.append(~Q(**{f"{field}__icontains": data}))
                    elif op == 'bw':  # begins with
                        q_objects.append(Q(**{f"{field}__istartswith": data}))
                    elif op == 'ew':  # ends with
                        q_objects.append(Q(**{f"{field}__iendswith": data}))
                
                if q_objects:
                    if group_op == 'OR':
                        query = q_objects[0]
                        for q in q_objects[1:]:
                            query |= q
                    else:  # AND
                        query = q_objects[0]
                        for q in q_objects[1:]:
                            query &= q
                    queryset = queryset.filter(query)
            except (json.JSONDecodeError, KeyError):
                pass
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def jqgrid_config(self, request, *args, **kwargs):
        """Override to ensure serializer_class is set"""
        try:
            # Store the dynamic serializer class
            self.serializer_class = self.get_serializer_class()
            # Store request for access in mixin
            self.request = request
            # Set queryset to ensure model is available
            self.queryset = self.get_queryset()
            # Call parent method
            return super().jqgrid_config(request, *args, **kwargs)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({
                'error': str(e),
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def bulk_action(self, request, *args, **kwargs):
        """Handle bulk actions"""
        action_type = request.data.get('action')
        ids = request.data.get('ids', [])
        
        if not action_type or not ids:
            return Response(
                {'error': 'Action and IDs are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        model = self.get_model()
        queryset = model.objects.filter(pk__in=ids)
        
        if action_type == 'delete':
            count = queryset.count()
            queryset.delete()
            return Response({'message': f'Deleted {count} items'})
        
        # Add more bulk actions as needed
        return Response(
            {'error': 'Unknown action'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'])
    def export(self, request, *args, **kwargs):
        """Export grid data"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        export_format = request.GET.get('format', 'json')
        
        if export_format == 'json':
            return Response(serializer.data)
        
        # Add CSV, Excel export as needed
        return Response(
            {'error': 'Unsupported format'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['post'])
    def import_data(self, request, *args, **kwargs):
        """Import data into grid"""
        # Implementation for data import
        return Response({'message': 'Import functionality not yet implemented'})
    
    @action(detail=False, methods=['get'])
    def dropdown(self, request, *args, **kwargs):
        """
        Return dropdown options for select fields
        Format: {"": "All", "1": "Option 1", "2": "Option 2", ...}
        """
        model = self.get_model()
        if not model:
            return Response({})
        
        # Get the field name from query params
        field_name = request.GET.get('field_name', '')
        
        # Get all objects
        queryset = self.get_queryset()
        
        # Build dropdown options
        options = {":": "All"}  # Default empty option
        
        for obj in queryset:
            # Get display value - try common patterns
            display_value = None
            
            # Try different methods to get a display value
            if hasattr(obj, 'get_display_name'):
                display_value = obj.get_display_name()
            elif hasattr(obj, 'name'):
                display_value = obj.name
            elif hasattr(obj, 'title'):
                display_value = obj.title
            elif hasattr(obj, '__str__'):
                display_value = str(obj)
            else:
                display_value = f"{model.__name__} {obj.pk}"
            
            options[str(obj.pk)] = display_value
        
        # Return in the format jqGrid expects
        return Response(options)
    
    @action(detail=True, methods=['get'])
    def dropdown_pk(self, request, pk=None, *args, **kwargs):
        """
        Return dropdown options for a specific record
        Used for editing existing records
        """
        return self.dropdown(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def additional_data_response(self, request, *args, **kwargs):
        """
        Return additional data for the grid
        Used for custom data that might be needed by the frontend
        """
        model = self.get_model()
        if not model:
            return Response({})
        
        # Initialize grid configuration to get additional data
        self.serializer_class = self.get_serializer_class()
        self.request = request
        self.queryset = self.get_queryset()
        
        # Initialize the grid to populate additional_data
        try:
            self.initgrid()
            additional_data = getattr(self, 'additional_data', {})
            return Response(additional_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
def get_content_type_info(request):
    """Get content type information for a model"""
    app_name = request.GET.get('app_name')
    model_name = request.GET.get('model')
    
    if not app_name or not model_name:
        return Response(
            {'error': 'Both app_name and model parameters are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        content_type = ContentType.objects.get(app_label=app_name, model=model_name)
        return Response({
            'id': content_type.id,
            'app_label': content_type.app_label,
            'model': content_type.model,
            'name': str(content_type),
        })
    except ContentType.DoesNotExist:
        return Response(
            {'error': f'Content type for {app_name}.{model_name} not found'},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
def get_grid_config(request, app_name, model_name):
    """API endpoint to get grid configuration"""
    try:
        model = apps.get_model(app_name, model_name)
    except LookupError:
        return Response(
            {'error': f'Model {app_name}.{model_name} not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Build grid configuration
    from .auto_config import get_grid_config_for_model
    config = get_grid_config_for_model(model)
    
    return Response(config)