#!/usr/bin/env python
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stitchflow.settings')
django.setup()

from etailoring.models import Accessory, GarmentType
from etailoring.serializers import AccessorySerializer

# Get the first accessory
accessory = Accessory.objects.first()

if accessory:
    print(f"Testing serialization of: {accessory.name}")
    print(f"ID: {accessory.id}")
    print(f"Applicable Garments: {list(accessory.applicable_garments.all().values_list('code', flat=True))}")
    
    # Serialize it
    serializer = AccessorySerializer(accessory)
    print(f"\nSerialized data:")
    print(json.dumps(serializer.data, indent=2, default=str))
else:
    print("No accessories found")
