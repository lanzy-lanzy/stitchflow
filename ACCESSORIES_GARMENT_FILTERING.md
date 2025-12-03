# Accessories Garment Filtering Implementation

## Overview
Accessories can now be assigned to specific garment types in the `manage_accessories.html` page. When creating an order in `create_order.html`, only accessories applicable to the selected garment type will be displayed.

## Changes Made

### 1. Backend (Already Implemented)
The backend already supports filtering accessories by garment type:
- **Model**: `Accessory` has a `ManyToManyField` called `applicable_garments` linked to `GarmentType`
- **Serializer**: `AccessorySerializer` includes `applicable_garments` field that returns garment codes
- **API View**: `AccessoryListCreateView` supports filtering via `?garment_type=CODE` query parameter

### 2. Frontend Changes

#### manage_accessories.html
- Already has proper UI for assigning accessories to garment types
- Modal form includes checkboxes for selecting applicable garments
- Save function collects selected garment codes and sends them to API
- Display shows which garments each accessory applies to

#### create_order.html

**Updated `loadAccessories()` function:**
- Now stores `applicable_garments` from API response in `data-applicableGarments` attribute
- Stores as comma-separated garment codes for easy client-side filtering
- Empty string means accessory is universal (applies to all garments)

**Updated `filterAccessoriesByGarment()` function:**
- Replaced keyword-based matching with proper garment code matching
- Now checks if selected garment type is in the `applicable_garments` list
- Universal accessories (empty `applicable_garments`) are always shown
- Unchecks checkboxes for hidden accessories to prevent submission

## How It Works

### For Admin Users (manage_accessories.html)

1. Click "Add Accessory" to create a new accessory
2. Fill in name, quantity, price, etc.
3. In "Applicable Garments" section, check one or more garment types
4. Leave unchecked to make it universal (applies to all garments)
5. Save - the selected garment codes are stored in the database

### For Order Creation (create_order.html)

1. Load order creation page
2. All accessories load from API (including `applicable_garments` field)
3. When user selects a garment type from the dropdown:
   - `filterAccessoriesByGarment()` is triggered
   - Only accessories with matching garment codes are shown
   - Universal accessories are always shown
4. User selects accessories and creates order

## Data Structure

**API Response for Accessory:**
```json
{
  "id": 1,
  "name": "Buttons",
  "description": "Pearl buttons",
  "quantity": 50,
  "price_per_unit": "2.50",
  "low_stock_threshold": 10,
  "is_low_stock": false,
  "applicable_garments": ["BLOUSE", "DRESS"]
}
```

**Universal Accessory (applies to all):**
```json
{
  "id": 2,
  "name": "Thread",
  "applicable_garments": []
}
```

## Garment Type Codes

Standard garment type codes in the system:
- `BLOUSE`
- `POLO`
- `PANTS`
- `SKIRT`
- `DRESS`
- `JACKET`

## Testing

### Manual Testing Steps:

1. **In manage_accessories.html:**
   - Create a new accessory
   - Assign it to specific garments (e.g., "BLOUSE" and "DRESS")
   - Save and verify it appears in the table with correct garment mappings

2. **In create_order.html:**
   - Select "BLOUSE" from garment type dropdown
   - Only accessories applicable to "BLOUSE" should be visible
   - Select "DRESS" and verify accessories update accordingly
   - Create an order and verify the correct accessories are submitted

### API Testing:

```bash
# Get all accessories
GET /api/admin/accessories/

# Get only BLOUSE accessories
GET /api/admin/accessories/?garment_type=BLOUSE

# Create with applicable garments
POST /api/admin/accessories/
{
  "name": "Lace",
  "quantity": 20,
  "price_per_unit": "5.00",
  "applicable_garments": ["BLOUSE", "DRESS"]
}
```

## Benefits

1. **Precise Filtering**: Users only see relevant accessories for their selected garment
2. **Improved UX**: Reduces clutter in the accessories selection
3. **Data Integrity**: Ensures only applicable accessories are attached to orders
4. **Flexibility**: Accessories can apply to multiple garments or be universal
5. **Scalability**: Easy to add new garment types and assign accessories to them

## Notes

- Accessories with empty `applicable_garments` are treated as universal and shown for all garment types
- The filtering happens on the client side after accessories are loaded from the API
- Unchecked accessories are automatically deselected when hidden to prevent form submission of hidden items
