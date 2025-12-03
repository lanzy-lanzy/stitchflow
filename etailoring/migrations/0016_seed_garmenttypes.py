from django.db import migrations


def create_garment_types(apps, schema_editor):
    GarmentType = apps.get_model('etailoring', 'GarmentType')
    # Seed basic garment types matching Order.GARMENT_TYPE_CHOICES
    items = [
        ('BLOUSE', 'Blouse'),
        ('POLO', 'Polo'),
        ('PANTS', 'Pants'),
        ('SKIRT', 'Skirt'),
        ('DRESS', 'Dress'),
        ('JACKET', 'Jacket'),
        ('OTHERS', 'Others'),
    ]
    for code, name in items:
        GarmentType.objects.update_or_create(code=code, defaults={'name': name})


def reverse_garment_types(apps, schema_editor):
    GarmentType = apps.get_model('etailoring', 'GarmentType')
    GarmentType.objects.filter(code__in=['BLOUSE', 'POLO', 'PANTS', 'SKIRT', 'DRESS', 'JACKET', 'OTHERS']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('etailoring', '0015_garmenttype_accessory_applicable_garments'),
    ]

    operations = [
        migrations.RunPython(create_garment_types, reverse_garment_types),
    ]
