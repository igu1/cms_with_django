from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.db import transaction
from .models import User, CustomerField, ColumnMapping, MappingField
import pandas as pd
import json

@login_required
def mapping_list(request):
    """View to list all column mappings"""
    if not request.user.is_manager():
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    mappings = ColumnMapping.objects.filter(created_by=request.user)
    
    context = {
        'mappings': mappings
    }
    
    return render(request, 'customer/mapping_list.html', context)

@login_required
def mapping_create(request):
    """View to create a new column mapping"""
    if not request.user.is_manager():
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        is_default = request.POST.get('is_default') == 'on'
        
        if not name:
            messages.error(request, 'Mapping name is required')
            return redirect('mapping_create')
        
        # If this is set as default, unset any other defaults
        if is_default:
            ColumnMapping.objects.filter(created_by=request.user, is_default=True).update(is_default=False)
        
        mapping = ColumnMapping.objects.create(
            name=name,
            description=description,
            is_default=is_default,
            created_by=request.user
        )
        
        messages.success(request, f'Mapping "{name}" created successfully')
        return redirect('mapping_edit', mapping_id=mapping.id)
    
    return render(request, 'customer/mapping_create.html')

@login_required
def mapping_edit(request, mapping_id):
    """View to edit a column mapping"""
    if not request.user.is_manager():
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    mapping = get_object_or_404(ColumnMapping, id=mapping_id, created_by=request.user)
    
    # Get all base fields from Customer model
    base_fields = [
        {'name': 'name', 'label': 'Name', 'required': True},
        {'name': 'phone_number', 'label': 'Phone Number', 'required': True},
        {'name': 'email', 'label': 'Email', 'required': False},
        {'name': 'address', 'label': 'Address', 'required': False},
        {'name': 'notes', 'label': 'Notes', 'required': False},
    ]
    
    # Get all custom fields
    custom_fields = CustomerField.objects.filter(active=True).values('name', 'label', 'required')
    
    # Get existing mapping fields
    mapping_fields = mapping.fields.all()
    
    if request.method == 'POST':
        # Handle form submission
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                data = json.loads(request.body)
                fields = data.get('fields', [])
                
                with transaction.atomic():
                    # Delete existing mapping fields
                    mapping.fields.all().delete()
                    
                    # Create new mapping fields
                    for field in fields:
                        MappingField.objects.create(
                            mapping=mapping,
                            csv_column=field['csv_column'],
                            field_type=field['field_type'],
                            field_name=field['field_name'],
                            is_required=field['is_required'],
                            default_value=field.get('default_value', '')
                        )
                    
                    # Update mapping details
                    mapping.name = data.get('name', mapping.name)
                    mapping.description = data.get('description', mapping.description)
                    mapping.is_default = data.get('is_default', mapping.is_default)
                    
                    # If this is set as default, unset any other defaults
                    if mapping.is_default:
                        ColumnMapping.objects.filter(created_by=request.user, is_default=True).exclude(id=mapping.id).update(is_default=False)
                    
                    mapping.save()
                
                return JsonResponse({'success': True})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        else:
            # Handle regular form submission
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            is_default = request.POST.get('is_default') == 'on'
            
            if not name:
                messages.error(request, 'Mapping name is required')
                return redirect('mapping_edit', mapping_id=mapping.id)
            
            # Update mapping details
            mapping.name = name
            mapping.description = description
            mapping.is_default = is_default
            
            # If this is set as default, unset any other defaults
            if is_default:
                ColumnMapping.objects.filter(created_by=request.user, is_default=True).exclude(id=mapping.id).update(is_default=False)
            
            mapping.save()
            
            messages.success(request, f'Mapping "{name}" updated successfully')
            return redirect('mapping_list')
    
    context = {
        'mapping': mapping,
        'base_fields': base_fields,
        'custom_fields': list(custom_fields),
        'mapping_fields': mapping_fields
    }
    
    return render(request, 'customer/mapping_edit.html', context)

@login_required
def mapping_delete(request, mapping_id):
    """View to delete a column mapping"""
    if not request.user.is_manager():
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    mapping = get_object_or_404(ColumnMapping, id=mapping_id, created_by=request.user)
    
    if request.method == 'POST':
        mapping_name = mapping.name
        mapping.delete()
        messages.success(request, f'Mapping "{mapping_name}" deleted successfully')
        return redirect('mapping_list')
    
    context = {
        'mapping': mapping
    }
    
    return render(request, 'customer/mapping_delete.html', context)

@login_required
def detect_csv_headers(request):
    """API to detect headers from a CSV file"""
    if not request.user.is_manager():
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    if request.method != 'POST' or 'file' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'No file provided'}, status=400)
    
    file = request.FILES['file']
    file_name = file.name
    file_ext = file_name.split('.')[-1].lower()
    
    if file_ext not in ['csv', 'xlsx']:
        return JsonResponse({'success': False, 'error': 'Only CSV and XLSX files are supported'}, status=400)
    
    try:
        # Read the first few rows to detect headers
        if file_ext == 'csv':
            df = pd.read_csv(file, nrows=5)
        else:  # xlsx
            df = pd.read_excel(file, nrows=5)
        
        headers = list(df.columns)
        preview = df.head(5).to_dict('records')
        
        return JsonResponse({
            'success': True, 
            'headers': headers,
            'preview': preview
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
