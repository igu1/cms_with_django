from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from .models import User, Customer, FileImport, CustomerStatusHistory, CustomerField, ColumnMapping, MappingField, FieldType

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )
    list_filter = UserAdmin.list_filter + ('role',)

class CustomerFieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'label', 'field_type', 'required', 'active', 'created_at')
    list_filter = ('field_type', 'required', 'active')
    search_fields = ('name', 'label')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'label', 'field_type', 'required', 'active')
        }),
        ('Advanced Options', {
            'classes': ('collapse',),
            'fields': ('default_value', 'options', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )

class MappingFieldInline(admin.TabularInline):
    model = MappingField
    extra = 1

class ColumnMappingAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_default', 'created_by', 'created_at', 'field_count')
    list_filter = ('is_default', 'created_by')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [MappingFieldInline]

    def field_count(self, obj):
        return obj.fields.count()
    field_count.short_description = 'Fields'

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'area', 'date', 'status', 'assigned_to', 'created_at', 'custom_fields')
    list_filter = ('status', 'assigned_to', 'date')
    search_fields = ('name', 'phone_number', 'email', 'area')
    date_hierarchy = 'created_at'
    readonly_fields = ('custom_data_display',)

    def custom_fields(self, obj):
        if not obj.custom_data:
            return '-'
        return format_html('<a href="#" onclick="return false;" title="{}">View {} fields</a>',
                          ', '.join([f'{k}: {v}' for k, v in obj.custom_data.items()]),
                          len(obj.custom_data))
    custom_fields.short_description = 'Custom Fields'

    def custom_data_display(self, obj):
        if not obj.custom_data:
            return '-'
        html = '<table style="width:100%"><tr><th>Field</th><th>Value</th></tr>'
        for key, value in obj.custom_data.items():
            html += f'<tr><td>{key}</td><td>{value}</td></tr>'
        html += '</table>'
        return format_html(html)
    custom_data_display.short_description = 'Custom Data'

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (None, {
                'fields': ('name', 'phone_number', 'email', 'address', 'area', 'date', 'status', 'assigned_to', 'remark', 'notes')
            }),
        ]

        if obj and obj.custom_data:
            fieldsets.append(('Custom Fields', {
                'fields': ('custom_data_display',)
            }))

        return fieldsets

class FileImportAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'imported_by', 'mapping_link', 'imported_at', 'total_records', 'successful_records', 'failed_records')
    list_filter = ('imported_by', 'mapping', 'imported_at')
    search_fields = ('file_name',)
    date_hierarchy = 'imported_at'

    def mapping_link(self, obj):
        if not obj.mapping:
            return '-'
        url = reverse('admin:customer_columnmapping_change', args=[obj.mapping.id])
        return format_html('<a href="{}">{}</a>', url, obj.mapping.name)
    mapping_link.short_description = 'Mapping'

class CustomerStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('customer', 'previous_status', 'new_status', 'changed_by', 'changed_at')
    list_filter = ('new_status', 'changed_by', 'changed_at')
    search_fields = ('customer__name', 'notes')
    date_hierarchy = 'changed_at'

admin.site.register(User, CustomUserAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(FileImport, FileImportAdmin)
admin.site.register(CustomerStatusHistory, CustomerStatusHistoryAdmin)
admin.site.register(CustomerField, CustomerFieldAdmin)
admin.site.register(ColumnMapping, ColumnMappingAdmin)
