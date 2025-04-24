from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0009_alter_customerstatushistory_options_followupreminder'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='phone_number',
            field=models.CharField(db_index=True, max_length=20, unique=True),
        ),
    ]
