# Fix: Applicable Garments Checkboxes Not Displaying

## Problem
The "Applicable Garments" section in the Edit/Add Accessory modal was showing an empty container with no checkboxes visible. Users couldn't assign accessories to garment types.

## Root Cause
In the `openAccessoryModal()` function, when garment types were loaded, the `populateGarmentOptions()` function was never called to render the checkboxes in the modal.

## Solution Applied

### Change 1: Ensure `populateGarmentOptions()` is called
**File**: `/templates/manage_accessories.html`
**Lines**: ~305-315

**Before**:
```javascript
if (!garmentTypes || garmentTypes.length === 0) {
    loadGarmentTypes().catch(err => console.warn('Could not load garment types:', err));
}
```

**After**:
```javascript
if (!garmentTypes || garmentTypes.length === 0) {
    loadGarmentTypes()
        .then(() => populateGarmentOptions())
        .catch(err => console.warn('Could not load garment types:', err));
} else {
    // Garment types already loaded, just populate the options
    populateGarmentOptions();
}
```

### Change 2: Add timing delay for checkbox population
**Lines**: ~325-365

Added 50ms delay using `setTimeout()` to ensure checkboxes are fully rendered before trying to select them. This prevents race conditions where the DOM elements don't exist yet.

**Before**:
```javascript
try {
    const checks = document.querySelectorAll('#applicableGarments .garment-checkbox');
    checks.forEach(cb => cb.checked = false);
    // ... more code
} catch (e) {
    console.warn('Could not populate applicable garments (checkboxes):', e);
}
```

**After**:
```javascript
setTimeout(() => {
    try {
        const checks = document.querySelectorAll('#applicableGarments .garment-checkbox');
        checks.forEach(cb => cb.checked = false);
        // ... more code
    } catch (e) {
        console.warn('Could not populate applicable garments (checkboxes):', e);
    }
}, 50);
```

## What This Fixes

✅ Checkboxes now appear when opening the modal
✅ Garment types display correctly with labels
✅ Can select/deselect garment types for accessories
✅ Edit mode pre-selects currently assigned garments
✅ Create mode starts with all checkboxes unchecked

## Testing Steps

1. Open Manage Accessories page
2. Click "Add Accessory" button
3. Verify checkboxes appear in "Applicable Garments" section
4. Check one or more garment types (e.g., BLOUSE, DRESS)
5. Save the accessory
6. Edit the same accessory
7. Verify the previously selected garments are still checked

## Files Modified

- `/templates/manage_accessories.html`
  - `openAccessoryModal()` function - Added proper `populateGarmentOptions()` calls
  - Added 50ms timing delays for safe DOM manipulation
