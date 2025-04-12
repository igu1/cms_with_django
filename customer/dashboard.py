from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from jazzmin.dashboard import Dashboard, modules
from .models import Customer, User, FileImport, CustomerStatusHistory, CustomerStatus


class CustomDashboard(Dashboard):
    """
    Custom dashboard for the admin panel
    """

    def init_with_context(self, context):
        # Get the current user
        user = context['request'].user

        # Get counts for various models
        total_customers = Customer.objects.count()
        total_users = User.objects.count()
        total_imports = FileImport.objects.count()
        total_status_changes = CustomerStatusHistory.objects.count()

        # Get counts for different customer statuses
        status_counts = {}
        for status, label in CustomerStatus.choices:
            count = Customer.objects.filter(status=status).count()
            status_counts[label] = count

        # Get recent activity
        recent_activity = CustomerStatusHistory.objects.select_related('customer', 'changed_by').order_by('-changed_at')[:10]

        # Get recent imports
        recent_imports = FileImport.objects.select_related('imported_by').order_by('-imported_at')[:5]

        # Get user activity
        user_activity = User.objects.annotate(
            status_changes=Count('status_changes', distinct=True),
            assigned_customers=Count('assigned_customers', distinct=True)
        ).order_by('-status_changes')[:5]

        # Get recent customers
        recent_customers = Customer.objects.select_related('assigned_to').order_by('-created_at')[:5]

        # Get statistics for the last 7 days
        last_week = timezone.now() - timedelta(days=7)
        new_customers_last_week = Customer.objects.filter(created_at__gte=last_week).count()
        status_changes_last_week = CustomerStatusHistory.objects.filter(changed_at__gte=last_week).count()

        # Add the dashboard modules
        self.children.append(modules.Group(
            _('Overview'),
            css_classes=('card-columns',),
            children=[
                modules.DashboardModule(
                    _('Customer Statistics'),
                    pre_content='<div class="row">'
                               '<div class="col-md-6">'
                               '<div class="info-box">'
                               '<span class="info-box-icon bg-info"><i class="fas fa-users"></i></span>'
                               '<div class="info-box-content">'
                               '<span class="info-box-text">Total Customers</span>'
                               f'<span class="info-box-number">{total_customers}</span>'
                               '</div>'
                               '</div>'
                               '</div>'
                               '<div class="col-md-6">'
                               '<div class="info-box">'
                               '<span class="info-box-icon bg-success"><i class="fas fa-user-plus"></i></span>'
                               '<div class="info-box-content">'
                               '<span class="info-box-text">New This Week</span>'
                               f'<span class="info-box-number">{new_customers_last_week}</span>'
                               '</div>'
                               '</div>'
                               '</div>'
                               '</div>',
                ),
                modules.DashboardModule(
                    _('User Statistics'),
                    pre_content='<div class="row">'
                               '<div class="col-md-6">'
                               '<div class="info-box">'
                               '<span class="info-box-icon bg-warning"><i class="fas fa-user-tie"></i></span>'
                               '<div class="info-box-content">'
                               '<span class="info-box-text">Total Users</span>'
                               f'<span class="info-box-number">{total_users}</span>'
                               '</div>'
                               '</div>'
                               '</div>'
                               '<div class="col-md-6">'
                               '<div class="info-box">'
                               '<span class="info-box-icon bg-danger"><i class="fas fa-history"></i></span>'
                               '<div class="info-box-content">'
                               '<span class="info-box-text">Status Changes</span>'
                               f'<span class="info-box-number">{status_changes_last_week} <small>this week</small></span>'
                               '</div>'
                               '</div>'
                               '</div>'
                               '</div>',
                ),
                modules.DashboardModule(
                    _('Customer Status Distribution'),
                    pre_content='<div id="status-chart" style="height: 300px;"></div>'
                               '<script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>'
                               '<script>'
                               'document.addEventListener("DOMContentLoaded", function() {'
                               '  var options = {'
                               '    series: [' + ', '.join(str(count) for count in status_counts.values()) + '],'
                               '    chart: {type: "donut", height: 300},'
                               '    labels: [' + ', '.join(f'"{label}"' for label in status_counts.keys()) + '],'
                               '    colors: ["#FFCDD2", "#C8E6C9", "#FFF9C4", "#E1BEE7", "#BBDEFB", "#CFD8DC", "#C5CAE9", "#B2DFDB", "#FFCC80", "#80CBC4", "#F8BBD0"],'
                               '    legend: {position: "bottom"},'
                               '    responsive: [{breakpoint: 480, options: {chart: {height: 250}, legend: {position: "bottom"}}}]'
                               '  };'
                               '  var chart = new ApexCharts(document.querySelector("#status-chart"), options);'
                               '  chart.render();'
                               '});'
                               '</script>',
                ),
            ]
        ))

        # Add recent activity module
        self.children.append(modules.Group(
            _('Recent Activity'),
            css_classes=('card-columns',),
            children=[
                modules.RecentActions(
                    _('My Recent Actions'),
                    limit=5,
                    include_list=('customer.customer', 'customer.user', 'customer.fileimport', 'customer.customerstatushistory'),
                ),
                modules.DashboardModule(
                    _('Recent Status Changes'),
                    children=(
                        {
                            'title': f"{item.customer.name} - {dict(CustomerStatus.choices).get(item.previous_status, 'None')} → {dict(CustomerStatus.choices).get(item.new_status, item.new_status)}",
                            'url': reverse('admin:customer_customerstatushistory_change', args=[item.id]),
                            'external': False,
                            'description': f"Changed by {item.changed_by.get_full_name() or item.changed_by.username} on {item.changed_at.strftime('%Y-%m-%d %H:%M')}",
                        } for item in recent_activity
                    ),
                ),
                modules.DashboardModule(
                    _('Recent File Imports'),
                    children=(
                        {
                            'title': f"{item.file_name}",
                            'url': reverse('admin:customer_fileimport_change', args=[item.id]),
                            'external': False,
                            'description': f"Imported by {item.imported_by.get_full_name() or item.imported_by.username} on {item.imported_at.strftime('%Y-%m-%d %H:%M')} - {item.successful_records}/{item.total_records} successful",
                        } for item in recent_imports
                    ),
                ),
            ]
        ))

        # Add quick links
        self.children.append(modules.LinkList(
            _('Quick Links'),
            draggable=False,
            deletable=False,
            collapsible=False,
            css_classes=('col-12',),
            children=[
                {
                    'title': _('Add New Customer'),
                    'url': reverse('admin:customer_customer_add'),
                    'external': False,
                    'description': _('Create a new customer record'),
                    'attrs': {'class': 'btn btn-success btn-block'},
                },
                {
                    'title': _('Add New User'),
                    'url': reverse('admin:customer_user_add'),
                    'external': False,
                    'description': _('Create a new user account'),
                    'attrs': {'class': 'btn btn-info btn-block'},
                },
                {
                    'title': _('View All Customers'),
                    'url': reverse('admin:customer_customer_changelist'),
                    'external': False,
                    'attrs': {'class': 'btn btn-primary btn-block'},
                },
                {
                    'title': _('View Status History'),
                    'url': reverse('admin:customer_customerstatushistory_changelist'),
                    'external': False,
                    'attrs': {'class': 'btn btn-secondary btn-block'},
                },
                {
                    'title': _('Go to Main Site'),
                    'url': '/',
                    'external': True,
                    'attrs': {'class': 'btn btn-warning btn-block', 'target': '_blank'},
                },
            ]
        ))
