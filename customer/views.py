from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Count, Q
from django.utils import timezone
from django.core.paginator import Paginator
from .models import User, Customer, FileImport, CustomerStatus, CustomerStatusHistory
from .forms import CustomerForm, CustomerStatusForm, CustomerAssignForm
import pandas as pd
import uuid
import os
import random

# Authentication Views
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'customer/login.html')

# Registration view removed

# Dashboard Views
@login_required
def dashboard(request):
    if request.user.is_manager():
        return manager_dashboard(request)
    else:
        return sales_dashboard(request)

@login_required
def manager_dashboard(request):
    if not request.user.is_manager():
        return HttpResponseForbidden("You don't have permission to access this page.")

    total_customers = Customer.objects.count()
    assigned_customers = Customer.objects.filter(assigned_to__isnull=False).count()
    unassigned_customers = Customer.objects.filter(assigned_to__isnull=True).count()

    # Get counts for each status
    status_counts = Customer.objects.values('status').annotate(count=Count('status'))
    status_data = {status['status']: status['count'] for status in status_counts}

    # Make sure all statuses are represented in the data, even if count is 0
    for status in CustomerStatus.values:
        if status not in status_data:
            status_data[status] = 0

    recent_imports = FileImport.objects.all()[:5]

    sales_users = User.objects.filter(role=User.SALES)
    sales_performance = []

    for user in sales_users:
        user_data = {
            'user': user,
            'assigned_count': Customer.objects.filter(assigned_to=user).count(),
            'status_counts': {}
        }

        for status in CustomerStatus.values:
            user_data['status_counts'][status] = Customer.objects.filter(
                assigned_to=user, status=status
            ).count()

        sales_performance.append(user_data)

    context = {
        'total_customers': total_customers,
        'assigned_customers': assigned_customers,
        'unassigned_customers': unassigned_customers,
        'status_data': status_data,
        'recent_imports': recent_imports,
        'sales_performance': sales_performance
    }

    return render(request, 'customer/manager_dashboard.html', context)

@login_required
def sales_dashboard(request):
    if not request.user.is_sales():
        return HttpResponseForbidden("You don't have permission to access this page.")

    assigned_customers = Customer.objects.filter(assigned_to=request.user).select_related('assigned_to')
    total_assigned = assigned_customers.count()

    # Get counts for each status
    status_counts = assigned_customers.values('status').annotate(count=Count('status'))
    status_data = {status['status']: status['count'] for status in status_counts}

    # Make sure all statuses are represented in the data, even if count is 0
    for status in CustomerStatus.values:
        if status not in status_data:
            status_data[status] = 0

    # Prepare status choices for the template
    statuses = [(status, label) for status, label in CustomerStatus.choices]

    # Get recent activity with optimized query
    recent_activity = CustomerStatusHistory.objects.filter(
        changed_by=request.user
    ).select_related('customer').order_by('-changed_at')[:10]

    # Pagination for assigned customers
    recent_customers = assigned_customers.order_by('-updated_at')
    paginator = Paginator(recent_customers, 10)  # Show 10 customers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'total_assigned': total_assigned,
        'status_data': status_data,
        'recent_activity': recent_activity,
        'assigned_customers': page_obj,
        'page_obj': page_obj,  # For pagination template
        'statuses': statuses
    }

    return render(request, 'customer/sales_dashboard.html', context)

# File Import Views
@login_required
def import_file(request):
    if not request.user.is_manager():
        return HttpResponseForbidden("You don't have permission to access this page.")

    if request.method == 'POST':
        if 'file' not in request.FILES:
            messages.error(request, 'Please select a file to upload')
            return redirect('import_file')

        file = request.FILES['file']
        file_name = file.name
        file_ext = os.path.splitext(file_name)[1].lower()

        if file_ext not in ['.xlsx', '.csv']:
            messages.error(request, 'Only XLSX and CSV files are supported')
            return redirect('import_file')

        # Create a temporary file to handle the upload
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            for chunk in file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        # Save the file import record
        file_import = FileImport.objects.create(
            file_name=file_name,
            file=file,
            imported_by=request.user
        )

        try:
            # Process the file
            if file_ext == '.xlsx':
                df = pd.read_excel(temp_file_path)
            else:  # CSV
                df = pd.read_csv(temp_file_path)

            # Clean up the temporary file
            os.unlink(temp_file_path)

            # Validate required columns
            required_columns = ['phone_number']
            for col in required_columns:
                if col not in df.columns:
                    messages.error(request, f'Required column {col} is missing')
                    file_import.delete()  # Delete the file import record
                    return redirect('import_file')

            # Process the data
            total_records = len(df)
            successful_records = 0
            failed_records = 0

            for _, row in df.iterrows():
                try:
                    # Check if customer with same phone number already exists
                    existing_customer = Customer.objects.filter(phone_number=row['phone_number']).first()

                    if existing_customer:
                        if 'name' in row and pd.notna(row['name']):
                            existing_customer.name = row['name']
                        else:
                            existing_customer.name = 'Unknown'
                        if 'area' in row and pd.notna(row['area']):
                            existing_customer.area = row['area']
                        if 'date' in row and pd.notna(row['date']):
                            existing_customer.date = row['date']
                        if 'remark' in row and pd.notna(row['remark']):
                            existing_customer.remark = row['remark']
                        existing_customer.save()
                    else:
                        # Create new customer
                        customer_data = {
                            'phone_number': row['phone_number']
                        }

                        if 'name' in row and pd.notna(row['name']):
                            customer_data['name'] = row['name']
                        else:
                            customer_data['name'] = 'Unknown'
                        if 'area' in row and pd.notna(row['area']):
                            customer_data['area'] = row['area']
                        if 'date' in row and pd.notna(row['date']):
                            customer_data['date'] = row['date']
                        if 'remark' in row and pd.notna(row['remark']):
                            customer_data['remark'] = row['remark']

                        Customer.objects.create(**customer_data)

                    successful_records += 1
                except Exception as e:
                    failed_records += 1
                    print(f"Error processing record: {e}")

            # Update file import record
            file_import.total_records = total_records
            file_import.successful_records = successful_records
            file_import.failed_records = failed_records
            file_import.save()

            messages.success(
                request,
                f'File imported successfully. {successful_records} records processed, {failed_records} failed.'
            )

        except Exception as e:
            messages.error(request, f'Error processing file: {str(e)}')
            file_import.delete()  # Delete the file import record
            # Clean up the temporary file if it still exists
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

        return redirect('import_history')

    return render(request, 'customer/import_file.html')

@login_required
def import_history(request):
    if not request.user.is_manager():
        return HttpResponseForbidden("You don't have permission to access this page.")

    imports = FileImport.objects.all().order_by('-imported_at')

    context = {
        'imports': imports
    }

    return render(request, 'customer/import_history.html', context)

# Customer Management Views
@login_required
def customer_list(request):
    # Use select_related to optimize the query for assigned_to
    if request.user.is_manager():
        customers = Customer.objects.select_related('assigned_to').all()
    else:
        customers = Customer.objects.select_related('assigned_to').filter(assigned_to=request.user)

    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'all':
        customers = customers.filter(status=status_filter)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        customers = customers.filter(
            Q(name__icontains=search_query) |
            Q(phone_number__icontains=search_query) |
            Q(area__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(customers, 25)  # Show 25 customers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'customers': page_obj,
        'page_obj': page_obj,  # For pagination template
        'statuses': CustomerStatus.choices,
        'current_status': status_filter,
        'search_query': search_query
    }

    return render(request, 'customer/customer_list.html', context)

@login_required
def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    # Check if user has permission to view this customer
    if not request.user.is_manager() and customer.assigned_to != request.user:
        return HttpResponseForbidden("You don't have permission to view this customer.")

    status_history = customer.status_history.all().order_by('-changed_at')

    # Initialize forms
    status_form = CustomerStatusForm(initial={'status': customer.status})
    assign_form = CustomerAssignForm(initial={'assigned_to': customer.assigned_to})

    context = {
        'customer': customer,
        'status_history': status_history,
        'statuses': CustomerStatus.choices,
        'status_form': status_form,
        'assign_form': assign_form,
        'sales_users': User.objects.filter(role=User.SALES)
    }

    return render(request, 'customer/customer_detail.html', context)

@login_required
def update_customer_status(request, customer_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    customer = get_object_or_404(Customer, id=customer_id)

    # Check if user has permission to update this customer
    if not request.user.is_manager() and customer.assigned_to != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    form = CustomerStatusForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': 'Invalid form data'}, status=400)

    new_status = form.cleaned_data['status']
    notes = form.cleaned_data['notes']

    if not new_status or new_status not in dict(CustomerStatus.choices):
        return JsonResponse({'error': 'Invalid status'}, status=400)

    previous_status = customer.status
    customer.status = new_status
    customer.save()

    # Create status history record
    CustomerStatusHistory.objects.create(
        customer=customer,
        previous_status=previous_status,
        new_status=new_status,
        changed_by=request.user,
        notes=notes
    )

    return JsonResponse({
        'success': True,
        'status': new_status,
        'status_display': dict(CustomerStatus.choices)[new_status]
    })

@login_required
def assign_customer(request, customer_id):
    if not request.user.is_manager():
        return JsonResponse({'error': 'Permission denied'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    customer = get_object_or_404(Customer, id=customer_id)
    sales_user_id = request.POST.get('sales_user')

    if sales_user_id:
        sales_user = get_object_or_404(User, id=sales_user_id, role=User.SALES)
        customer.assigned_to = sales_user
    else:
        customer.assigned_to = None

    customer.save()

    return JsonResponse({
        'success': True,
        'assigned_to': customer.assigned_to.username if customer.assigned_to else None
    })

@login_required
def unassigned_customers(request):
    if not request.user.is_manager():
        return HttpResponseForbidden("You don't have permission to access this page.")

    customers = Customer.objects.filter(assigned_to__isnull=True).order_by('-created_at')
    sales_users = User.objects.filter(role=User.SALES)

    # Pagination
    paginator = Paginator(customers, 25)  # Show 25 customers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'customers': page_obj,
        'page_obj': page_obj,  # For pagination template
        'sales_users': sales_users
    }

    return render(request, 'customer/unassigned_customers.html', context)

@login_required
def bulk_assign_customers(request):
    if not request.user.is_manager() or request.method != 'POST':
        return HttpResponseForbidden("You don't have permission to access this page.")

    sales_user_id = request.POST.get('sales_user')
    customer_ids = request.POST.getlist('customer_ids')

    if not sales_user_id or not customer_ids:
        messages.error(request, 'Please select a student counsellor and at least one customer')
        return redirect('unassigned_customers')

    sales_user = get_object_or_404(User, id=sales_user_id, role=User.SALES)

    # Update customers
    Customer.objects.filter(id__in=customer_ids).update(assigned_to=sales_user)

    messages.success(
        request,
        f'{len(customer_ids)} customers assigned to {sales_user.username}'
    )

    return redirect('unassigned_customers')

@login_required
def random_assign_customers(request):
    if not request.user.is_manager() or request.method != 'POST':
        return HttpResponseForbidden("You don't have permission to access this page.")

    sales_users = list(User.objects.filter(role=User.SALES))
    if not sales_users:
        messages.error(request, 'No student counsellors available for assignment')
        return redirect('unassigned_customers')

    customer_ids = request.POST.getlist('customer_ids')
    if not customer_ids:
        messages.error(request, 'Please select at least one customer')
        return redirect('unassigned_customers')

    # Assign customers randomly
    for customer_id in customer_ids:
        sales_user = random.choice(sales_users)
        Customer.objects.filter(id=customer_id).update(assigned_to=sales_user)

    messages.success(
        request,
        f'{len(customer_ids)} customers randomly assigned to student counsellors'
    )

    return redirect('unassigned_customers')
