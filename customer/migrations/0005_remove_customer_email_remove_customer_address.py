from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0004_remove_columnmapping_created_by_delete_customerfield_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='email',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='address',
        ),
    ]
