# Accessory to Garment Type Assignment - Fixed

## Issue Summary
The accessory management system was not properly saving garment type assignments. All accessories were showing as "All" garments (universal) even when specific garments were selected during creation/editing.

## Root Causes

### 1. Backend Filter Issue (views.py)
**Problem**: The `AccessoryListCreateView.get_queryset()` method used `Q(applicable_garments__isnull=True)` to check for accessories with no garment assignments. This doesn't work correctly with Django's ManyToMany fields, as the relationship table itself is never NULL.

**Fix**: Changed the filter to use `Count('applicable_garments')` annotation:
```python
from django.db.models import Count
qs = qs.annotate(garment_count=Count('applicable_garments')).filter(
    Q(applicable_garments__code__iexact=garment) | Q(garment_count=0)
).distinct()
```

### 2. Serializer M2M Handling Issue (serializers.py)
**Problem**: The `AccessorySerializer` relied on the default ModelSerializer behavior for M2M fields. During POST/PUT operations, the M2M relationship wasn't being properly saved, even though the SlugRelatedField was configured correctly.

**Fix**: Added explicit `create()` and `update()` methods to handle the `applicable_garments` M2M field:
```python
def create(self, validated_data):
    """Create accessory with applicable garments."""
    applicable_garments = validated_data.pop('applicable_garments', [])
    accessory = Accessory.objects.create(**validated_data)
    
    if applicable_garments:
        accessory.applicable_garments.set(applicable_garments)
    
    return accessory

def update(self, instance, validated_data):
    """Update accessory with applicable garments."""
    applicable_garments = validated_data.pop('applicable_garments', None)
    
    for attr, value in validated_data.items():
        setattr(instance, attr, value)
    
    instance.save()
    
    if applicable_garments is not None:
        instance.applicable_garments.set(applicable_garments)
    
    return instance
```

## UI Behavior (Working Correctly)
The frontend template (`manage_accessories.html`) was already correctly implemented:
- Checkboxes send garment codes (e.g., ['BLOUSE', 'POLO'])
- Display logic maps codes to garment names
- Shows "All" when no specific garments are assigned

## Testing

### To verify the fix works:

1. **Create a new accessory** with specific garments selected:
   - Navigate to Manage Accessories
   - Click "Add Accessory"
   - Fill in the form
   - Check only specific garment types (e.g., BLOUSE, POLO)
   - Save

2. **Expected results**:
   - The "Garments" column should display the selected garment names (not "All")
   - When editing, the checkboxes should be pre-checked for the previously selected garments

3. **Database verification**:
   ```sql
   SELECT a.id, a.name, GROUP_CONCAT(g.code, ', ') as garments
   FROM etailoring_accessory a
   LEFT JOIN etailoring_accessory_applicable_garments ag ON a.id = ag.accessory_id
   LEFT JOIN etailoring_garmenttype g ON ag.garmenttype_id = g.id
   GROUP BY a.id;
   ```
   - Non-universal accessories should show their specific garment codes
   - Universal accessories should show NULL/empty garments

## Files Modified
1. `etailoring/views.py` - Fixed AccessoryListCreateView.get_queryset()
2. `etailoring/serializers.py` - Added create() and update() methods to AccessorySerializer

## Backward Compatibility
- Existing universal accessories (with no garments assigned) will continue to work as before
- The filter correctly identifies them as applicable to any garment type
- All existing APIs and UI remain compatible
