# Generated migration for increasing phone number field length

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etailoring', '0013_remove_accessories_preference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='phone_number',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='tailor',
            name='phone_number',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='userextension',
            name='phone_number',
            field=models.CharField(max_length=20),
        ),
    ]
