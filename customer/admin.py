from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Customer, FileImport, CustomerStatusHistory

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )
    list_filter = UserAdmin.list_filter + ('role',)

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'email', 'assigned_to', 'status', 'created_at')
    list_filter = ('status', 'assigned_to')
    search_fields = ('name', 'phone_number', 'email')
    date_hierarchy = 'created_at'

class FileImportAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'imported_by', 'imported_at', 'total_records', 'successful_records', 'failed_records')
    list_filter = ('imported_by', 'imported_at')
    search_fields = ('file_name',)
    date_hierarchy = 'imported_at'

class CustomerStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('customer', 'previous_status', 'new_status', 'changed_by', 'changed_at')
    list_filter = ('new_status', 'changed_by', 'changed_at')
    search_fields = ('customer__name', 'notes')
    date_hierarchy = 'changed_at'

admin.site.register(User, CustomUserAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(FileImport, FileImportAdmin)
admin.site.register(CustomerStatusHistory, CustomerStatusHistoryAdmin)
