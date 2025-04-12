from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
import uuid
import json

class User(AbstractUser):
    MANAGER = 'manager'
    SALES = 'sales'

    ROLE_CHOICES = [
        (MANAGER, 'Manager'),
        (SALES, 'Sales'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=SALES)

    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        related_name='customer_user_set',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        related_name='customer_user_set',
        related_query_name='user',
    )

    def is_manager(self):
        return self.role == self.MANAGER

    def is_sales(self):
        return self.role == self.SALES

class CustomerStatus(models.TextChoices):
    CALLED = 'CALLED', _('Called')
    NOT_ANSWERED = 'NOT_ANSWERED', _('Not Answered')
    INVALID_NUMBER = 'INVALID_NUMBER', _('Invalid Number')
    PLAN_PRESENTED = 'PLAN_PRESENTED', _('Plan Presented')
    SHORTLISTED = 'SHORTLISTED', _('Shortlisted')

class FieldType(models.TextChoices):
    TEXT = 'TEXT', _('Text')
    NUMBER = 'NUMBER', _('Number')
    EMAIL = 'EMAIL', _('Email')
    PHONE = 'PHONE', _('Phone')
    DATE = 'DATE', _('Date')
    BOOLEAN = 'BOOLEAN', _('Boolean')
    SELECT = 'SELECT', _('Select')

class CustomerField(models.Model):
    name = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=255)
    field_type = models.CharField(max_length=20, choices=FieldType.choices, default=FieldType.TEXT)
    required = models.BooleanField(default=False)
    default_value = models.TextField(blank=True, null=True)
    options = models.TextField(blank=True, null=True, help_text='Comma-separated options for SELECT field type')
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.label} ({self.field_type})"

    def get_options_list(self):
        if not self.options:
            return []
        return [option.strip() for option in self.options.split(',')]

    class Meta:
        ordering = ['name']
        verbose_name = 'Custom Field'
        verbose_name_plural = 'Custom Fields'

class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_customers')
    status = models.CharField(
        max_length=20,
        choices=CustomerStatus.choices,
        default=None,
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True, null=True)
    custom_data = models.JSONField(default=dict, blank=True, encoder=DjangoJSONEncoder)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_custom_field_value(self, field_name):
        return self.custom_data.get(field_name, None)

    def set_custom_field_value(self, field_name, value):
        custom_data = self.custom_data.copy()
        custom_data[field_name] = value
        self.custom_data = custom_data

    class Meta:
        ordering = ['-created_at']

class ColumnMapping(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_default = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='column_mappings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

class MappingField(models.Model):
    FIELD_TYPES = [
        ('base', 'Base Field'),
        ('custom', 'Custom Field')
    ]

    mapping = models.ForeignKey(ColumnMapping, on_delete=models.CASCADE, related_name='fields')
    csv_column = models.CharField(max_length=255)
    field_type = models.CharField(max_length=10, choices=FIELD_TYPES)
    field_name = models.CharField(max_length=255)
    is_required = models.BooleanField(default=False)
    default_value = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.csv_column} -> {self.field_name}"

    class Meta:
        unique_together = ('mapping', 'csv_column')
        ordering = ['mapping', 'csv_column']

class FileImport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_name = models.CharField(max_length=255)
    file = models.FileField(upload_to='imports/')
    imported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='file_imports')
    mapping = models.ForeignKey(ColumnMapping, on_delete=models.SET_NULL, null=True, blank=True, related_name='imports')
    imported_at = models.DateTimeField(auto_now_add=True)
    total_records = models.IntegerField(default=0)
    successful_records = models.IntegerField(default=0)
    failed_records = models.IntegerField(default=0)

    def __str__(self):
        return self.file_name

    class Meta:
        ordering = ['-imported_at']

class CustomerStatusHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='status_history')
    previous_status = models.CharField(max_length=20, choices=CustomerStatus.choices, null=True, blank=True)
    new_status = models.CharField(max_length=20, choices=CustomerStatus.choices)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='status_changes')
    changed_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.customer.name} - {self.new_status}"

    class Meta:
        ordering = ['-changed_at']
