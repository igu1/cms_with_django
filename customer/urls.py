from django.urls import path
from . import views
from . import views_mapping
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Dashboard URLs
    path('', views.dashboard, name='dashboard'),

    # File Import URLs
    path('import/', views.import_file, name='import_file'),
    path('import/history/', views.import_history, name='import_history'),
    path('import/detect-headers/', views_mapping.detect_csv_headers, name='detect_csv_headers'),

    # Column Mapping URLs
    path('mappings/', views_mapping.mapping_list, name='mapping_list'),
    path('mappings/create/', views_mapping.mapping_create, name='mapping_create'),
    path('mappings/<int:mapping_id>/edit/', views_mapping.mapping_edit, name='mapping_edit'),
    path('mappings/<int:mapping_id>/delete/', views_mapping.mapping_delete, name='mapping_delete'),

    # Customer Management URLs
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<uuid:customer_id>/', views.customer_detail, name='customer_detail'),
    path('customers/<uuid:customer_id>/update-status/', views.update_customer_status, name='update_customer_status'),
    path('customers/<uuid:customer_id>/assign/', views.assign_customer, name='assign_customer'),
    path('customers/unassigned/', views.unassigned_customers, name='unassigned_customers'),
    path('customers/bulk-assign/', views.bulk_assign_customers, name='bulk_assign_customers'),
    path('customers/random-assign/', views.random_assign_customers, name='random_assign_customers'),
]
