from django.urls import path
from . import views
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
    path('customers/unassigned/', views.unassigned_customers, name='unassigned_customers'),
    path('customers/bulk-assign/', views.bulk_assign_customers, name='bulk_assign_customers'),
    path('customers/random-assign/', views.random_assign_customers, name='random_assign_customers'),
]
