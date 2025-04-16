from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.admin import AdminSite
from .models import (
    User, Customer, FileImport, CustomerStatusHistory, CustomerStatus,
    CustomerNote, NoteCategory, Task, TaskComment, TaskPriority, TaskStatus
)

# Custom admin site
class CustomAdminSite(AdminSite):
    site_header = 'ALIMS.CO.IN Administration'
    site_title = 'ALIMS.CO.IN Admin Portal'
    index_title = 'Welcome to ALIMS.CO.IN Admin Portal'
    
    def index(self, request, extra_context=None):
        # Get statistics for the dashboard
        app_list = self.get_app_list(request)
        
        # Customer statistics
        customer_count = Customer.objects.count()
        valid_count = Customer.objects.filter(status='VALID').count()
        interested_count = Customer.objects.filter(status='INTERESTED').count()
        admission_count = Customer.objects.filter(status='ADMISSION').count()
        
        # Task statistics
        from django.utils import timezone
        task_count = Task.objects.count()
        pending_task_count = Task.objects.filter(status='PENDING').count()
        completed_task_count = Task.objects.filter(status='COMPLETED').count()
        overdue_task_count = Task.objects.filter(
            status='PENDING',
            due_date__lt=timezone.now()
        ).count()
        
        # User statistics
        user_count = User.objects.count()
        manager_count = User.objects.filter(role=User.MANAGER).count()
        counsellor_count = User.objects.filter(role=User.SALES).count()
        active_user_count = User.objects.filter(is_active=True).count()
        
        context = {
            **self.each_context(request),
            'title': self.index_title,
            'app_list': app_list,
            'customer_count': customer_count,
            'valid_count': valid_count,
            'interested_count': interested_count,
            'admission_count': admission_count,
            'task_count': task_count,
            'pending_task_count': pending_task_count,
            'completed_task_count': completed_task_count,
            'overdue_task_count': overdue_task_count,
            'user_count': user_count,
            'manager_count': manager_count,
            'counsellor_count': counsellor_count,
            'active_user_count': active_user_count,
            **(extra_context or {}),
        }
        
        return super().index(request, context)

# Create custom admin site instance
admin_site = CustomAdminSite(name='admin')

# Register site header, title, and index title for default admin site
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

class CustomerNoteInline(admin.TabularInline):
    model = CustomerNote
    extra = 1
    fields = ('category', 'content', 'created_by', 'created_at', 'is_pinned')
    readonly_fields = ('created_at',)
    verbose_name = 'Note'
    verbose_name_plural = 'Notes'

class CustomerNoteAdmin(admin.ModelAdmin):
    list_display = ('customer_link', 'category_badge', 'note_preview', 'created_by', 'created_at', 'is_pinned')
    list_filter = ('category', 'created_by', 'created_at', 'is_pinned')
    search_fields = ('content', 'customer__name', 'customer__phone_number')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    
    fieldsets = [
        (_('Note Information'), {
            'fields': ('customer', 'category', 'content', 'is_pinned')
        }),
        (_('System Information'), {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',),
        }),
    ]
    
    def customer_link(self, obj):
        url = reverse('admin:customer_customer_change', args=[obj.customer.id])
        return format_html('<a href="{}">{}</a>', url, obj.customer.name)
    
    customer_link.short_description = 'Customer'
    customer_link.admin_order_field = 'customer__name'
    
    def note_preview(self, obj):
        if len(obj.content) > 50:
            return obj.content[:50] + '...'
        return obj.content
    
    note_preview.short_description = 'Content'
    
    def category_badge(self, obj):
        category_styles = {
            'GENERAL': {'bg': '#E0E0E0', 'color': '#616161', 'icon': 'fas fa-sticky-note'},
            'CALL': {'bg': '#BBDEFB', 'color': '#1565C0', 'icon': 'fas fa-phone'},
            'MEETING': {'bg': '#C8E6C9', 'color': '#2E7D32', 'icon': 'fas fa-handshake'},
            'FOLLOW_UP': {'bg': '#C5CAE9', 'color': '#283593', 'icon': 'fas fa-calendar-check'},
            'CAMPUS_VISIT': {'bg': '#FFCC80', 'color': '#EF6C00', 'icon': 'fas fa-building'},
            'DOCUMENT': {'bg': '#E1BEE7', 'color': '#6A1B9A', 'icon': 'fas fa-file-alt'},
            'PAYMENT': {'bg': '#80CBC4', 'color': '#00796B', 'icon': 'fas fa-money-bill'},
            'OTHER': {'bg': '#CFD8DC', 'color': '#455A64', 'icon': 'fas fa-question-circle'},
        }
        
        style = category_styles.get(obj.category, {'bg': '#E0E0E0', 'color': '#616161', 'icon': 'fas fa-sticky-note'})
        label = dict(NoteCategory.choices).get(obj.category, obj.category)
        
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 3px 8px; border-radius: 10px; font-size: 0.8em;">' +
            '<i class="{}"></i> {}' +
            '</span>',
            style['bg'], style['color'], style['icon'], label
        )
    
    category_badge.short_description = 'Category'
    category_badge.admin_order_field = 'category'

class TaskCommentInline(admin.TabularInline):
    model = TaskComment
    extra = 1
    fields = ('author', 'content', 'created_at')
    readonly_fields = ('created_at',)
    verbose_name = 'Comment'
    verbose_name_plural = 'Comments'

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'customer_link', 'priority_badge', 'status_badge', 'due_date_display', 'assigned_to_link', 'created_by', 'created_at')
    list_filter = ('status', 'priority', 'assigned_to', 'created_by', 'created_at', 'due_date')
    search_fields = ('title', 'description', 'customer__name', 'customer__phone_number')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    inlines = [TaskCommentInline]
    
    fieldsets = [
        (_('Task Information'), {
            'fields': ('title', 'description', 'customer')
        }),
        (_('Assignment & Priority'), {
            'fields': ('assigned_to', 'priority', 'status', 'due_date')
        }),
        (_('System Information'), {
            'fields': ('created_by', 'created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',),
        }),
    ]
    
    def changelist_view(self, request, extra_context=None):
        """Add current time to the context for the task list view."""
        from django.utils import timezone
        
        extra_context = extra_context or {}
        extra_context['now'] = timezone.now()
        
        return super().changelist_view(request, extra_context)
    
    def customer_link(self, obj):
        url = reverse('admin:customer_customer_change', args=[obj.customer.id])
        return format_html('<a href="{}">{}</a>', url, obj.customer.name)
    
    customer_link.short_description = 'Customer'
    customer_link.admin_order_field = 'customer__name'
    
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
    
    def priority_badge(self, obj):
        priority_styles = {
            'LOW': {'bg': '#E0E0E0', 'color': '#616161', 'icon': 'fas fa-arrow-down'},
            'MEDIUM': {'bg': '#BBDEFB', 'color': '#1565C0', 'icon': 'fas fa-minus'},
            'HIGH': {'bg': '#FFCC80', 'color': '#EF6C00', 'icon': 'fas fa-arrow-up'},
            'URGENT': {'bg': '#FFCDD2', 'color': '#C62828', 'icon': 'fas fa-exclamation-circle'},
        }
        
        style = priority_styles.get(obj.priority, {'bg': '#E0E0E0', 'color': '#616161', 'icon': 'fas fa-question-circle'})
        label = dict(TaskPriority.choices).get(obj.priority, obj.priority)
        
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 3px 8px; border-radius: 10px; font-size: 0.8em;">' +
            '<i class="{}"></i> {}' +
            '</span>',
            style['bg'], style['color'], style['icon'], label
        )
    
    priority_badge.short_description = 'Priority'
    priority_badge.admin_order_field = 'priority'
    
    def status_badge(self, obj):
        status_styles = {
            'PENDING': {'bg': '#FFF9C4', 'color': '#F57F17', 'icon': 'fas fa-clock'},
            'IN_PROGRESS': {'bg': '#BBDEFB', 'color': '#1565C0', 'icon': 'fas fa-spinner'},
            'COMPLETED': {'bg': '#C8E6C9', 'color': '#2E7D32', 'icon': 'fas fa-check'},
            'DEFERRED': {'bg': '#E1BEE7', 'color': '#6A1B9A', 'icon': 'fas fa-pause-circle'},
            'CANCELLED': {'bg': '#CFD8DC', 'color': '#455A64', 'icon': 'fas fa-ban'},
        }
        
        style = status_styles.get(obj.status, {'bg': '#E0E0E0', 'color': '#616161', 'icon': 'fas fa-question-circle'})
        label = dict(TaskStatus.choices).get(obj.status, obj.status)
        
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 3px 8px; border-radius: 10px; font-size: 0.8em;">' +
            '<i class="{}"></i> {}' +
            '</span>',
            style['bg'], style['color'], style['icon'], label
        )
    
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def due_date_display(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        
        if not obj.due_date:
            return '-'
        
        # Calculate time remaining
        now = timezone.now()
        time_remaining = obj.due_date - now
        
        # Format the countdown
        if obj.status == 'COMPLETED' or obj.status == 'CANCELLED':
            date_str = obj.due_date.strftime('%Y-%m-%d %H:%M')
            if obj.status == 'COMPLETED':
                icon = '<i class="fas fa-check-circle"></i>'
                color = '#2E7D32'
            else:
                icon = '<i class="fas fa-ban"></i>'
                color = '#455A64'
            return format_html(
                '<span style="color: {};">{} {}</span>',
                color, date_str, icon
            )
        elif obj.is_overdue():
            # Overdue
            days_overdue = abs(time_remaining.days)
            hours_overdue = abs(time_remaining.seconds) // 3600
            
            if days_overdue > 0:
                overdue_text = f"Overdue by {days_overdue}d {hours_overdue}h"
            else:
                overdue_text = f"Overdue by {hours_overdue}h"
                
            return format_html(
                '<div><span style="color: #C62828; font-weight: bold;">{}</span></div>' +
                '<div><span class="task-countdown overdue" style="color: #C62828; font-size: 0.8em;"><i class="fas fa-exclamation-triangle"></i> {}</span></div>',
                obj.due_date.strftime('%Y-%m-%d %H:%M'), overdue_text
            )
        elif obj.is_due_soon():
            # Due soon (within 24 hours)
            hours_left = time_remaining.seconds // 3600
            minutes_left = (time_remaining.seconds % 3600) // 60
            
            if time_remaining.days > 0:
                countdown = f"{time_remaining.days}d {hours_left}h left"
            elif hours_left > 0:
                countdown = f"{hours_left}h {minutes_left}m left"
            else:
                countdown = f"{minutes_left}m left"
                
            return format_html(
                '<div><span style="color: #F57F17; font-weight: bold;">{}</span></div>' +
                '<div><span class="task-countdown due-soon" style="color: #F57F17; font-size: 0.8em;"><i class="fas fa-clock"></i> {}</span></div>',
                obj.due_date.strftime('%Y-%m-%d %H:%M'), countdown
            )
        else:
            # Not due soon
            days_left = time_remaining.days
            hours_left = time_remaining.seconds // 3600
            
            countdown = f"{days_left}d {hours_left}h left"
            
            return format_html(
                '<div>{}</div>' +
                '<div><span class="task-countdown upcoming" style="color: #1565C0; font-size: 0.8em;"><i class="fas fa-calendar-alt"></i> {}</span></div>',
                obj.due_date.strftime('%Y-%m-%d %H:%M'), countdown
            )
    
    due_date_display.short_description = 'Due Date'
    due_date_display.admin_order_field = 'due_date'

class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('task_link', 'comment_preview', 'author', 'created_at')
    list_filter = ('author', 'created_at')
    search_fields = ('content', 'task__title', 'author__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    
    fieldsets = [
        (_('Comment Information'), {
            'fields': ('task', 'content', 'author')
        }),
        (_('System Information'), {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    ]
    
    def task_link(self, obj):
        url = reverse('admin:customer_task_change', args=[obj.task.id])
        return format_html('<a href="{}">{}</a>', url, obj.task.title)
    
    task_link.short_description = 'Task'
    task_link.admin_order_field = 'task__title'
    
    def comment_preview(self, obj):
        if len(obj.content) > 50:
            return obj.content[:50] + '...'
        return obj.content
    
    comment_preview.short_description = 'Content'

# Update the Customer admin to include notes inline
CustomerAdmin.inlines = [CustomerStatusHistoryInline, CustomerNoteInline]

# Register models with both admin sites
for admin_site_instance in [admin.site, admin_site]:
    admin_site_instance.register(User, CustomUserAdmin)
    admin_site_instance.register(Customer, CustomerAdmin)
    admin_site_instance.register(FileImport, FileImportAdmin)
    admin_site_instance.register(CustomerStatusHistory, CustomerStatusHistoryAdmin)
    admin_site_instance.register(CustomerNote, CustomerNoteAdmin)
    admin_site_instance.register(Task, TaskAdmin)
    admin_site_instance.register(TaskComment, TaskCommentAdmin)

