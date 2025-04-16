from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NoteCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='CustomerNote',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('category', models.CharField(choices=[('GENERAL', 'General'), ('CALL', 'Call Notes'), ('MEETING', 'Meeting Notes'), ('FOLLOW_UP', 'Follow-up'), ('CAMPUS_VISIT', 'Campus Visit'), ('DOCUMENT', 'Documentation'), ('PAYMENT', 'Payment'), ('OTHER', 'Other')], default='GENERAL', max_length=20, db_index=True)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
                ('is_pinned', models.BooleanField(default=False)),
                ('customer', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='notes_history', to='customer.Customer')),
                ('created_by', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='customer_notes', to='customer.User')),
            ],
            options={
                'ordering': ['-is_pinned', '-created_at'],
            },
        ),
    ]