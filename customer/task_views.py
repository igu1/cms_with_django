from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator
from .models import User, Customer, Task, TaskStatus, TaskPriority, TaskComment
from .forms import TaskForm, TaskCommentForm, TaskFilterForm
from datetime import datetime, timedelta

# Task Management Views
@login_required
def task_list(request):
    """View for listing all tasks"""
    # Initialize the filter form
    filter_form = TaskFilterForm(request.GET, user=request.user)
    
    # Start with all tasks
    if request.user.is_manager():
        tasks = Task.objects.all()
    else:
        # Sales users can only see tasks assigned to them or created by them
        tasks = Task.objects.filter(
            Q(assigned_to=request.user) | Q(created_by=request.user)
        ).distinct()
    
    # Apply filters
    if filter_form.is_valid():
        status = filter_form.cleaned_data.get('status')
        priority = filter_form.cleaned_data.get('priority')
        assigned_to = filter_form.cleaned_data.get('assigned_to')
        due_date_from = filter_form.cleaned_data.get('due_date_from')
        due_date_to = filter_form.cleaned_data.get('due_date_to')
        search = filter_form.cleaned_data.get('search')
        
        if status:
            tasks = tasks.filter(status=status)
        
        if priority:
            tasks = tasks.filter(priority=priority)
        
        if assigned_to:
            tasks = tasks.filter(assigned_to=assigned_to)
        
        if due_date_from:
            tasks = tasks.filter(due_date__gte=due_date_from)
        
        if due_date_to:
            # Add one day to include the end date
            due_date_to = datetime.combine(due_date_to, datetime.max.time())
            tasks = tasks.filter(due_date__lte=due_date_to)
        
        if search:
            tasks = tasks.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) |
                Q(customer__name__icontains=search)
            )
    
    # Get counts for dashboard
    total_tasks = tasks.count()
    pending_tasks = tasks.filter(status=TaskStatus.PENDING).count()
    in_progress_tasks = tasks.filter(status=TaskStatus.IN_PROGRESS).count()
    completed_tasks = tasks.filter(status=TaskStatus.COMPLETED).count()
    
    # Calculate overdue tasks
    now = timezone.now()
    overdue_tasks = tasks.filter(
        due_date__lt=now,
        status__in=[TaskStatus.PENDING, TaskStatus.IN_PROGRESS]
    ).count()
    
    # Calculate due soon tasks (within 24 hours)
    tomorrow = now + timedelta(days=1)
    due_soon_tasks = tasks.filter(
        due_date__gte=now,
        due_date__lt=tomorrow,
        status__in=[TaskStatus.PENDING, TaskStatus.IN_PROGRESS]
    ).count()
    
    # Order tasks
    tasks = tasks.select_related('customer', 'assigned_to', 'created_by').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(tasks, 20)  # Show 20 tasks per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tasks': page_obj,
        'filter_form': filter_form,
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks,
        'due_soon_tasks': due_soon_tasks,
        'page_obj': page_obj,
        'page_title': 'Task Management'
    }
    
    return render(request, 'customer/task_list.html', context)


@login_required
def customer_tasks(request, customer_id):
    """View for listing tasks for a specific customer"""
    customer = get_object_or_404(Customer, id=customer_id)
    
    # Check if user has permission to view this customer's tasks
    if not request.user.is_manager() and customer.assigned_to != request.user:
        return HttpResponseForbidden("You don't have permission to view this customer's tasks.")
    
    # Get all tasks for this customer
    tasks = Task.objects.filter(customer=customer).select_related('assigned_to', 'created_by').order_by('-created_at')
    
    # Initialize the task form
    task_form = TaskForm(user=request.user)
    
    if request.method == 'POST':
        task_form = TaskForm(request.POST, user=request.user)
        if task_form.is_valid():
            task = task_form.save(commit=False)
            task.customer = customer
            task.created_by = request.user
            
            # If no assigned_to is specified and user is not a manager, assign to self
            if not task.assigned_to and not request.user.is_manager():
                task.assigned_to = request.user
                
            task.save()
            messages.success(request, 'Task created successfully.')
            return redirect('customer_tasks', customer_id=customer_id)
    
    context = {
        'customer': customer,
        'tasks': tasks,
        'task_form': task_form,
        'page_title': f'Tasks for {customer.name}'
    }
    
    return render(request, 'customer/customer_tasks.html', context)


@login_required
def task_detail(request, task_id):
    """View for viewing and updating a specific task"""
    task = get_object_or_404(Task, id=task_id)
    
    # Check if user has permission to view this task
    if not request.user.is_manager() and task.assigned_to != request.user and task.created_by != request.user:
        return HttpResponseForbidden("You don't have permission to view this task.")
    
    # Get all comments for this task
    comments = task.comments.all().select_related('author').order_by('created_at')
    
    # Initialize the comment form
    comment_form = TaskCommentForm()
    
    if request.method == 'POST':
        # Handle comment submission
        if 'add_comment' in request.POST:
            comment_form = TaskCommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.task = task
                comment.author = request.user
                comment.save()
                messages.success(request, 'Comment added successfully.')
                return redirect('task_detail', task_id=task_id)
        
        # Handle task status update
        elif 'update_status' in request.POST:
            new_status = request.POST.get('status')
            if new_status in dict(TaskStatus.choices):
                task.status = new_status
                if new_status == TaskStatus.COMPLETED and not task.completed_at:
                    task.completed_at = timezone.now()
                task.save()
                messages.success(request, f'Task status updated to {dict(TaskStatus.choices)[new_status]}.')
                return redirect('task_detail', task_id=task_id)
    
    context = {
        'task': task,
        'comments': comments,
        'comment_form': comment_form,
        'task_statuses': TaskStatus.choices,
        'page_title': task.title
    }
    
    return render(request, 'customer/task_detail.html', context)


@login_required
def edit_task(request, task_id):
    """View for editing a task"""
    task = get_object_or_404(Task, id=task_id)
    
    # Check if user has permission to edit this task
    if not request.user.is_manager() and task.created_by != request.user:
        return HttpResponseForbidden("You don't have permission to edit this task.")
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully.')
            return redirect('task_detail', task_id=task_id)
    else:
        form = TaskForm(instance=task, user=request.user)
    
    context = {
        'form': form,
        'task': task,
        'page_title': f'Edit Task: {task.title}'
    }
    
    return render(request, 'customer/edit_task.html', context)


@login_required
def delete_task(request, task_id):
    """View for deleting a task"""
    task = get_object_or_404(Task, id=task_id)
    
    # Check if user has permission to delete this task
    if not request.user.is_manager() and task.created_by != request.user:
        return HttpResponseForbidden("You don't have permission to delete this task.")
    
    if request.method == 'POST':
        customer_id = task.customer.id
        task.delete()
        messages.success(request, 'Task deleted successfully.')
        
        # Redirect back to the customer's tasks page
        return redirect('customer_tasks', customer_id=customer_id)
    
    context = {
        'task': task,
        'page_title': f'Delete Task: {task.title}'
    }
    
    return render(request, 'customer/delete_task.html', context)


@login_required
def complete_task(request, task_id):
    """AJAX view for marking a task as complete"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    task = get_object_or_404(Task, id=task_id)
    
    # Check if user has permission to update this task
    if not request.user.is_manager() and task.assigned_to != request.user and task.created_by != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    task.status = TaskStatus.COMPLETED
    task.completed_at = timezone.now()
    task.save()
    
    return JsonResponse({
        'success': True,
        'task_id': str(task.id),
        'completed_at': task.completed_at.strftime('%Y-%m-%d %H:%M')
    })


@login_required
def my_tasks(request):
    """View for showing tasks assigned to the current user"""
    # Get tasks assigned to the current user
    tasks = Task.objects.filter(assigned_to=request.user).select_related('customer', 'created_by').order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter and status_filter in dict(TaskStatus.choices):
        tasks = tasks.filter(status=status_filter)
    
    # Calculate overdue and due soon tasks
    now = timezone.now()
    overdue_tasks = tasks.filter(
        due_date__lt=now,
        status__in=[TaskStatus.PENDING, TaskStatus.IN_PROGRESS]
    )
    
    tomorrow = now + timedelta(days=1)
    due_soon_tasks = tasks.filter(
        due_date__gte=now,
        due_date__lt=tomorrow,
        status__in=[TaskStatus.PENDING, TaskStatus.IN_PROGRESS]
    )
    
    # Pagination
    paginator = Paginator(tasks, 20)  # Show 20 tasks per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tasks': page_obj,
        'overdue_tasks': overdue_tasks,
        'due_soon_tasks': due_soon_tasks,
        'task_statuses': TaskStatus.choices,
        'current_status': status_filter,
        'page_obj': page_obj,
        'page_title': 'My Tasks'
    }
    
    return render(request, 'customer/my_tasks.html', context)