from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

class FileImport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_name = models.CharField(max_length=255)
    file = models.FileField(upload_to='imports/')
    imported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='file_imports')
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
