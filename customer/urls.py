from django.urls import path
from . import views
from . import task_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Dashboard URLs
    path('', views.dashboard, name='dashboard'),

    # File Import URLs
    path('import/', views.import_file, name='import_file'),
    path('import/history/', views.import_history, name='import_history'),


    # Customer Management URLs
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<uuid:customer_id>/', views.customer_detail, name='customer_detail'),
    path('customers/<uuid:customer_id>/update-status/', views.update_customer_status, name='update_customer_status'),
    path('customers/<uuid:customer_id>/assign/', views.assign_customer, name='assign_customer'),
    path('customers/<uuid:customer_id>/add-note/', views.add_customer_note, name='add_customer_note'),
    path('customers/notes/<uuid:note_id>/delete/', views.delete_customer_note, name='delete_customer_note'),
    path('customers/notes/<uuid:note_id>/toggle-pin/', views.toggle_pin_note, name='toggle_pin_note'),
    path('customers/unassigned/', views.unassigned_customers, name='unassigned_customers'),
    path('customers/bulk-assign/', views.bulk_assign_customers, name='bulk_assign_customers'),
    path('customers/random-assign/', views.random_assign_customers, name='random_assign_customers'),
    path('customers/bulk-status-update/', views.bulk_status_update, name='bulk_status_update'),
    path('customer-status/', views.customer_status, name='customer_status'),
    
    # Task Management URLs
    path('tasks/', task_views.task_list, name='task_list'),
    path('tasks/my-tasks/', task_views.my_tasks, name='my_tasks'),
    path('tasks/<uuid:task_id>/', task_views.task_detail, name='task_detail'),
    path('tasks/<uuid:task_id>/edit/', task_views.edit_task, name='edit_task'),
    path('tasks/<uuid:task_id>/delete/', task_views.delete_task, name='delete_task'),
    path('tasks/<uuid:task_id>/complete/', task_views.complete_task, name='complete_task'),
    path('customers/<uuid:customer_id>/tasks/', task_views.customer_tasks, name='customer_tasks'),
]
