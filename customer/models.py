from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
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

    def __str__(self):
        return self.phone_number

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

class NoteCategory(models.TextChoices):
    GENERAL = 'GENERAL', _('General')
    CALL = 'CALL', _('Call Notes')
    MEETING = 'MEETING', _('Meeting Notes')
    FOLLOW_UP = 'FOLLOW_UP', _('Follow-up')
    CAMPUS_VISIT = 'CAMPUS_VISIT', _('Campus Visit')
    DOCUMENT = 'DOCUMENT', _('Documentation')
    PAYMENT = 'PAYMENT', _('Payment')
    OTHER = 'OTHER', _('Other')

class CustomerNote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='notes_history', db_index=True)
    category = models.CharField(max_length=20, choices=NoteCategory.choices, default=NoteCategory.GENERAL, db_index=True)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_notes', db_index=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    is_pinned = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.customer.name} - {self.category} - {self.created_at.strftime('%Y-%m-%d')}"
    
    class Meta:
        ordering = ['-is_pinned', '-created_at']


class TaskPriority(models.TextChoices):
    LOW = 'LOW', _('Low')
    MEDIUM = 'MEDIUM', _('Medium')
    HIGH = 'HIGH', _('High')
    URGENT = 'URGENT', _('Urgent')


class TaskStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
    COMPLETED = 'COMPLETED', _('Completed')
    DEFERRED = 'DEFERRED', _('Deferred')
    CANCELLED = 'CANCELLED', _('Cancelled')


class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='tasks', db_index=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks', db_index=True)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks', db_index=True, null=True, blank=True)
    priority = models.CharField(max_length=10, choices=TaskPriority.choices, default=TaskPriority.MEDIUM, db_index=True)
    status = models.CharField(max_length=15, choices=TaskStatus.choices, default=TaskStatus.PENDING, db_index=True)
    due_date = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.title
    
    def is_overdue(self):
        if self.due_date and self.status != TaskStatus.COMPLETED and self.status != TaskStatus.CANCELLED:
            return timezone.now() > self.due_date
        return False
    
    def is_due_soon(self):
        if self.due_date and self.status != TaskStatus.COMPLETED and self.status != TaskStatus.CANCELLED:
            return timezone.now() + timedelta(days=1) > self.due_date
        return False
    
    def complete(self):
        self.status = TaskStatus.COMPLETED
        self.completed_at = timezone.now()
        self.save()
    
    class Meta:
        ordering = ['-created_at']


class TaskComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_comments')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Comment on {self.task.title} by {self.author.username}"
    
    class Meta:
        ordering = ['created_at']
