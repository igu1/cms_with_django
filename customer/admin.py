from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from .models import User, Customer, FileImport, CustomerStatusHistory, CustomerStatus

# Register site header, title, and index title
admin.site.site_header = 'ALIMS.CO.IN Administration'
admin.site.site_title = 'ALIMS.CO.IN Admin Portal'
admin.site.index_title = 'Welcome to ALIMS.CO.IN Admin Portal'

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role_badge', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Role'), {'fields': ('role',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'first_name', 'last_name', 'role'),
        }),
    )

    def role_badge(self, obj):
        if obj.role == User.MANAGER:
            return format_html('<span style="background-color: #4CAF50; color: white; padding: 3px 8px; border-radius: 10px; font-size: 0.8em;"><i class="fas fa-user-tie"></i> Sales Manager</span>')
        else:
            return format_html('<span style="background-color: #2196F3; color: white; padding: 3px 8px; border-radius: 10px; font-size: 0.8em;"><i class="fas fa-user-graduate"></i> Student Counsellor</span>')

    role_badge.short_description = 'Role'
    role_badge.admin_order_field = 'role'

class CustomerStatusHistoryInline(admin.TabularInline):
    model = CustomerStatusHistory
    extra = 0
    readonly_fields = ('previous_status', 'new_status', 'changed_by', 'changed_at')
    can_delete = False
    verbose_name = 'Status History'
    verbose_name_plural = 'Status History'

    def has_add_permission(self, request, obj=None):
        return False

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'area', 'date', 'status_badge', 'assigned_to_link', 'created_at')
    list_filter = ('status', 'assigned_to', 'date', 'created_at')
    search_fields = ('name', 'phone_number', 'area', 'notes', 'remark')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CustomerStatusHistoryInline]
    list_per_page = 25
    save_on_top = True

    fieldsets = [
        (_('Basic Information'), {
            'fields': ('name', 'phone_number', 'area', 'date')
        }),
        (_('Status & Assignment'), {
            'fields': ('status', 'assigned_to')
        }),
        (_('Additional Information'), {
            'fields': ('remark', 'notes')
        }),
        (_('System Information'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    ]

    def status_badge(self, obj):
        if not obj.status:
            return format_html('<span style="background-color: #E0E0E0; color: #616161; padding: 3px 8px; border-radius: 10px; font-size: 0.8em;"><i class="fas fa-question-circle"></i> No Status</span>')

        status_styles = {
            'INVALID': {'bg': '#FFCDD2', 'color': '#C62828', 'icon': 'fas fa-times-circle'},
            'VALID': {'bg': '#C8E6C9', 'color': '#2E7D32', 'icon': 'fas fa-check-circle'},
            'CALL_NOT_ATTENDED': {'bg': '#FFF9C4', 'color': '#F57F17', 'icon': 'fas fa-phone-slash'},
            'PLAN_PRESENTED': {'bg': '#E1BEE7', 'color': '#6A1B9A', 'icon': 'fas fa-file-alt'},
            'INTERESTED': {'bg': '#BBDEFB', 'color': '#1565C0', 'icon': 'fas fa-thumbs-up'},
            'NOT_INTERESTED': {'bg': '#CFD8DC', 'color': '#455A64', 'icon': 'fas fa-thumbs-down'},
            'FOLLOW_UP': {'bg': '#C5CAE9', 'color': '#283593', 'icon': 'fas fa-calendar-check'},
            'SHORTLISTED': {'bg': '#B2DFDB', 'color': '#00695C', 'icon': 'fas fa-star'},
            'CAMPUS_VISIT': {'bg': '#FFCC80', 'color': '#EF6C00', 'icon': 'fas fa-building'},
            'REGISTRATION': {'bg': '#80CBC4', 'color': '#00796B', 'icon': 'fas fa-clipboard-list'},
            'ADMISSION': {'bg': '#F8BBD0', 'color': '#AD1457', 'icon': 'fas fa-graduation-cap'},
        }

        style = status_styles.get(obj.status, {'bg': '#E0E0E0', 'color': '#616161', 'icon': 'fas fa-question-circle'})
        label = dict(CustomerStatus.choices).get(obj.status, obj.status)

        return format_html(
            '<span style="background-color: {}; color: {}; padding: 3px 8px; border-radius: 10px; font-size: 0.8em;">' +
            '<i class="{}"></i> {}' +
            '</span>',
            style['bg'], style['color'], style['icon'], label
        )

    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    def assigned_to_link(self, obj):
        if obj.assigned_to:
            url = reverse('admin:customer_user_change', args=[obj.assigned_to.id])
            if obj.assigned_to.role == User.MANAGER:
                icon = 'fas fa-user-tie'
                style = 'background-color: #4CAF50; color: white;'
            else:
                icon = 'fas fa-user-graduate'
                style = 'background-color: #2196F3; color: white;'

            return format_html('<a href="{}" style="{}; padding: 3px 8px; border-radius: 10px; font-size: 0.8em;">' +
                              '<i class="{}"></i> {}' +
                              '</a>',
                              url, style, icon, obj.assigned_to.get_full_name() or obj.assigned_to.username)
        return '-'

    assigned_to_link.short_description = 'Assigned To'
    assigned_to_link.admin_order_field = 'assigned_to'

class FileImportAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'imported_by', 'imported_at', 'success_rate', 'total_records')
    list_filter = ('imported_by', 'imported_at')
    search_fields = ('file_name',)
    date_hierarchy = 'imported_at'
    readonly_fields = ('imported_at', 'total_records', 'successful_records', 'failed_records')

    fieldsets = [
        (_('File Information'), {
            'fields': ('file_name', 'file')
        }),
        (_('Import Details'), {
            'fields': ('imported_by', 'imported_at')
        }),
        (_('Results'), {
            'fields': ('total_records', 'successful_records', 'failed_records')
        }),
    ]

    def success_rate(self, obj):
        if obj.total_records == 0:
            rate = 0
        else:
            rate = (obj.successful_records / obj.total_records) * 100

        # Format the rate as a string with one decimal place
        formatted_rate = f"{rate:.1f}"

        if rate >= 90:
            color = 'green'
        elif rate >= 70:
            color = 'orange'
        else:
            color = 'red'

        return format_html('<span style="color: {}; font-weight: bold;">{}%</span> ({}/{})',
                          color, formatted_rate, obj.successful_records, obj.total_records)

    success_rate.short_description = 'Success Rate'

class CustomerStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('customer_link', 'status_change', 'changed_by', 'changed_at')
    list_filter = ('new_status', 'previous_status', 'changed_by', 'changed_at')
    search_fields = ('customer__name', 'notes', 'customer__phone_number')
    date_hierarchy = 'changed_at'
    readonly_fields = ('customer', 'previous_status', 'new_status', 'changed_by', 'changed_at')

    fieldsets = [
        (_('Status Change'), {
            'fields': ('customer', 'previous_status', 'new_status')
        }),
        (_('Change Information'), {
            'fields': ('changed_by', 'changed_at', 'notes')
        }),
    ]

    def customer_link(self, obj):
        url = reverse('admin:customer_customer_change', args=[obj.customer.id])
        return format_html('<a href="{}">{}</a>', url, obj.customer.name)

    customer_link.short_description = 'Customer'
    customer_link.admin_order_field = 'customer__name'

    def status_change(self, obj):
        status_styles = {
            'INVALID': {'bg': '#FFCDD2', 'color': '#C62828', 'icon': 'fas fa-times-circle'},
            'VALID': {'bg': '#C8E6C9', 'color': '#2E7D32', 'icon': 'fas fa-check-circle'},
            'CALL_NOT_ATTENDED': {'bg': '#FFF9C4', 'color': '#F57F17', 'icon': 'fas fa-phone-slash'},
            'PLAN_PRESENTED': {'bg': '#E1BEE7', 'color': '#6A1B9A', 'icon': 'fas fa-file-alt'},
            'INTERESTED': {'bg': '#BBDEFB', 'color': '#1565C0', 'icon': 'fas fa-thumbs-up'},
            'NOT_INTERESTED': {'bg': '#CFD8DC', 'color': '#455A64', 'icon': 'fas fa-thumbs-down'},
            'FOLLOW_UP': {'bg': '#C5CAE9', 'color': '#283593', 'icon': 'fas fa-calendar-check'},
            'SHORTLISTED': {'bg': '#B2DFDB', 'color': '#00695C', 'icon': 'fas fa-star'},
            'CAMPUS_VISIT': {'bg': '#FFCC80', 'color': '#EF6C00', 'icon': 'fas fa-building'},
            'REGISTRATION': {'bg': '#80CBC4', 'color': '#00796B', 'icon': 'fas fa-clipboard-list'},
            'ADMISSION': {'bg': '#F8BBD0', 'color': '#AD1457', 'icon': 'fas fa-graduation-cap'},
        }

        if obj.previous_status:
            prev_style = status_styles.get(obj.previous_status, {'bg': '#E0E0E0', 'color': '#616161', 'icon': 'fas fa-question-circle'})
            prev_label = dict(CustomerStatus.choices).get(obj.previous_status, obj.previous_status)
            prev_badge = format_html(
                '<span style="background-color: {}; color: {}; padding: 3px 8px; border-radius: 10px; font-size: 0.8em; margin-right: 5px;">' +
                '<i class="{}"></i> {}' +
                '</span>',
                prev_style['bg'], prev_style['color'], prev_style['icon'], prev_label
            )
        else:
            prev_badge = format_html(
                '<span style="background-color: #E0E0E0; color: #616161; padding: 3px 8px; border-radius: 10px; font-size: 0.8em; margin-right: 5px;">' +
                '<i class="fas fa-question-circle"></i> None' +
                '</span>'
            )

        new_style = status_styles.get(obj.new_status, {'bg': '#E0E0E0', 'color': '#616161', 'icon': 'fas fa-question-circle'})
        new_label = dict(CustomerStatus.choices).get(obj.new_status, obj.new_status)
        new_badge = format_html(
            '<span style="background-color: {}; color: {}; padding: 3px 8px; border-radius: 10px; font-size: 0.8em;">' +
            '<i class="{}"></i> {}' +
            '</span>',
            new_style['bg'], new_style['color'], new_style['icon'], new_label
        )

        return format_html('{} <i class="fas fa-arrow-right" style="margin: 0 5px;"></i> {}', prev_badge, new_badge)

    status_change.short_description = 'Status Change'

# Register models with the admin site
admin.site.register(User, CustomUserAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(FileImport, FileImportAdmin)
admin.site.register(CustomerStatusHistory, CustomerStatusHistoryAdmin)

