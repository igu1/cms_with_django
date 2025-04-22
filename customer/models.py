from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid

class User(AbstractUser):
    MANAGER = 'manager'
    SALES = 'sales'

    ROLE_CHOICES = [
        (MANAGER, 'Sales Manager'),
        (SALES, 'Student Counsellor'),
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
    INVALID = 'INVALID', _('Invalid')
    VALID = 'VALID', _('Valid')
    CALL_NOT_ATTENDED = 'CALL_NOT_ATTENDED', _('Call Not Attended')
    PLAN_PRESENTED = 'PLAN_PRESENTED', _('Plan Presented')
    INTERESTED = 'INTERESTED', _('Interested')
    NOT_INTERESTED = 'NOT_INTERESTED', _('Not Interested')
    FOLLOW_UP = 'FOLLOW_UP', _('Follow Up')
    SHORTLISTED = 'SHORTLISTED', _('Shortlisted')
    CAMPUS_VISIT = 'CAMPUS_VISIT', _('Campus Visit')
    REGISTRATION = 'REGISTRATION', _('Registration')
    ADMISSION = 'ADMISSION', _('Admission')



class CustomerManager(models.Manager):
    def get_queryset(self):
        # Using Case/When to handle null values in ordering
        from django.db.models import Case, When, Value, IntegerField
        return super().get_queryset().annotate(
            name_null=Case(
                When(name__isnull=True, then=Value(1)),
                When(name='', then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            )
        ).order_by('name_null', 'name', '-created_at')

class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, db_index=True, null=True, blank=True)
    phone_number = models.CharField(max_length=20, db_index=True)
    area = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    date = models.DateField(blank=True, null=True, db_index=True)
    remark = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_customers', db_index=True)
    status = models.CharField(
        max_length=20,
        choices=CustomerStatus.choices,
        default=None,
        null=True,
        blank=True,
        db_index=True
    )
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = CustomerManager()

    def __str__(self):
        return self.phone_number

    class Meta:
        # We can't use complex ordering in Meta, so we'll rely on the manager
        # This is a fallback ordering
        ordering = ['name', '-created_at']



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
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='status_history', db_index=True)
    previous_status = models.CharField(max_length=20, choices=CustomerStatus.choices, null=True, blank=True, db_index=True)
    new_status = models.CharField(max_length=20, choices=CustomerStatus.choices, db_index=True)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='status_changes', db_index=True)
    changed_at = models.DateTimeField(default=timezone.now, db_index=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.customer.name} - {self.new_status}"

    class Meta:
        ordering = ['-changed_at']
