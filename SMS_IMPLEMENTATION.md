# SMS Notification Implementation

## Overview
This document outlines the SMS notification feature implemented using **Semaphore API** for StitchFlow. The system automatically sends SMS notifications to customers when their garments are ready for pickup after task approval.

## Features
- **Customer Notifications**: Automatically notify customers via SMS when their garment is ready for pickup
- **Error Handling**: Gracefully handles SMS failures without disrupting task approval
- **Logging**: All SMS operations are logged for debugging and monitoring
- **Configuration**: Easy setup via environment variables

## Setup Instructions

### 1. Install Dependencies
The SMS service uses the `requests` library. Ensure it's in your requirements.txt:
```bash
pip install requests
```

### 2. Get Semaphore API Key
1. Visit [Semaphore.co](https://semaphore.co)
2. Sign up for an account
3. Get your API key from the dashboard
4. Note: Semaphore provides free credits for testing

### 3. Configure Environment Variables
Set your Semaphore API key in one of these ways:

**Option A: Environment Variable (Recommended for Production)**
```bash
export SEMAPHORE_API_KEY="your-api-key-here"
```

**Option B: Django Settings** (settings.py already configured)
The settings.py file includes:
```python
SEMAPHORE_API_KEY = os.getenv('SEMAPHORE_API_KEY', 'your-api-key-here')
SEMAPHORE_SENDER_NAME = 'StitchFlow'
```

**Option C: Direct Configuration** (Development only)
Edit `stitchflow/settings.py`:
```python
SEMAPHORE_API_KEY = 'your-actual-api-key'
SEMAPHORE_SENDER_NAME = 'StitchFlow'
```

### 4. Test the Setup
Use the management command to test SMS functionality:

```bash
# Test with a phone number
python manage.py test_sms 09998887777

# Test with custom customer name and order ID
python manage.py test_sms 09998887777 --customer-name "Juan Dela Cruz" --order-id 42
```

## Files Modified/Created

### New Files:
1. **etailoring/sms_service.py**
   - `SemaphoreSMS` class with SMS sending methods
   - `notify_customer_ready_for_pickup()` - Sends customer pickup notification
   - `notify_tailor_commission_ready()` - Sends tailor commission notification (future use)

2. **etailoring/management/commands/test_sms.py**
   - Management command for testing SMS functionality

### Modified Files:
1. **stitchflow/settings.py**
   - Added `SEMAPHORE_API_KEY` configuration
   - Added `SEMAPHORE_SENDER_NAME` configuration

2. **etailoring/views.py**
   - Updated `approve_task()` function to send SMS notifications
   - Added SMS error handling (doesn't fail task approval if SMS fails)

3. **templates/manage_tasks.html**
   - Updated success message to include "Customer notified via SMS"

## Implementation Details

### SMS Service (sms_service.py)

#### `SemaphoreSMS.send_message(message, number)`
Generic SMS sending method:
- **Parameters:**
  - `message` (str): The message content
  - `number` (str): Phone number (e.g., 09998887777)
- **Returns:** `(success: bool, response_data: dict or error_message: str)`
- **Features:**
  - Validates API key and phone number
  - Handles network errors gracefully
  - Logs all operations
  - 10-second timeout for API requests

#### `SemaphoreSMS.notify_customer_ready_for_pickup(customer_name, customer_phone, order_id)`
Sends pickup notification to customer:
- **Parameters:**
  - `customer_name` (str): Customer's full name
  - `customer_phone` (str): Customer's phone number
  - `order_id` (int): Order ID
- **Message Format:** 
  ```
  Hi {name}, your garment for Order #{order_id} is ready for pickup at El Senior Dumingag. Thank you!
  ```

### Task Approval Flow with SMS

When a task is approved in `views.py`:
1. Task status is changed to APPROVED
2. Commission is created for the tailor
3. SMS notification is sent to the customer
4. Even if SMS fails, the task approval succeeds (non-blocking)
5. Error details are logged for later review

```
Task Approval → Commission Created → SMS Sent → Response to Admin
                                        ↓
                                   (if fails)
                                   Log Error
```

## Error Handling

The SMS service includes comprehensive error handling:

### API Key Missing
```
Error: Semaphore API key not configured
Action: Logged as ERROR, SMS not sent
Result: Task approval continues
```

### Phone Number Invalid
```
Error: Phone number not provided
Action: Logged as ERROR, SMS not sent
Result: Task approval continues
```

### Network Timeout
```
Error: SMS API request timeout
Action: Logged as ERROR, SMS not sent
Result: Task approval continues
```

### API Response Error
```
Error: SMS API returned status {code}
Action: Logged as ERROR with response details
Result: Task approval continues
```

## Message Examples

### Customer Pickup Notification
```
Hi Maria Santos, your garment for Order #15 is ready for pickup at El Senior Dumingag. Thank you!
```

### Tailor Commission Notification (Future)
```
Hi Jose Cruz, commission of ₱500.00 for Order #15 has been approved. Please contact admin for payment.
```

## Logging

All SMS operations are logged to the Django logger. View logs:

```python
# In Django shell or application logs
import logging
logger = logging.getLogger(__name__)

# SMS service logs at:
# - INFO level: Successful SMS sends
# - WARNING level: Recoverable errors
# - ERROR level: Critical failures
```

Example log messages:
```
INFO: SMS sent to 09998887777. Status: 200
INFO: Successfully sent ready-for-pickup SMS to 09998887777
WARNING: Failed to send SMS to 09998887777: API returned 401
ERROR: Semaphore API key not configured
ERROR: Error sending SMS notification for task 42: Connection timeout
```

## Troubleshooting

### Issue: "SMS API key not configured"
**Solution:** 
- Ensure `SEMAPHORE_API_KEY` is set in environment variables
- Check `stitchflow/settings.py` configuration
- Restart Django application after setting environment variables

### Issue: "SMS API request timeout"
**Solution:**
- Check your internet connection
- Verify Semaphore API status (https://semaphore.co)
- Try again after a few seconds
- Check if API key is valid

### Issue: "SMS API returned status 401"
**Solution:**
- Verify API key is correct
- Check if API key has expired
- Generate a new API key from Semaphore dashboard

### Issue: "Phone number not provided"
**Solution:**
- Ensure customer record has phone number in database
- Check phone number format is valid
- Use format: 09998887777 or +639998887777

## Phone Number Formats Supported

Semaphore accepts:
- Philippine Format: `09998887777`
- International Format: `+639998887777`
- Other countries: Check Semaphore documentation

## Future Enhancements

1. **SMS History Tracking**
   - Add SMSLog model to track sent messages
   - Track delivery status and timestamps

2. **Additional Notifications**
   - Tailor commission notifications
   - Order completion reminders
   - Payment reminders

3. **Bulk Messaging**
   - Send notifications to multiple customers
   - Scheduled reminder campaigns

4. **Message Templates**
   - Customizable message templates
   - Multi-language support

5. **Retry Logic**
   - Automatic retry for failed SMS
   - Exponential backoff strategy

## API Documentation References

- Semaphore API Docs: https://semaphore.co/api/v4/messages
- Semaphore Dashboard: https://semaphore.co/dashboard

## Testing Checklist

- [ ] API key is set and valid
- [ ] Test SMS sends successfully via management command
- [ ] Task approval triggers SMS notification
- [ ] Customer phone number is present in database
- [ ] SMS logs are recorded correctly
- [ ] SMS failures don't block task approval
- [ ] Error messages are informative in logs

## Security Considerations

1. **API Key Security:**
   - Never commit API key to repository
   - Use environment variables in production
   - Rotate API keys periodically

2. **Phone Number Privacy:**
   - Phone numbers are only used for SMS notifications
   - Not stored elsewhere or shared
   - Comply with data protection regulations

3. **Audit Trail:**
   - All SMS sends are logged
   - Includes timestamp, phone number, order ID
   - Useful for compliance and debugging

## Support

For issues with:
- **Semaphore API**: Contact Semaphore support or check their documentation
- **StitchFlow Integration**: Check logs and error messages
- **Phone Numbers**: Verify format and validity

## Summary

The SMS implementation provides:
✓ Automatic customer notifications when garments are ready
✓ Error handling that doesn't disrupt workflow
✓ Easy configuration via environment variables
✓ Comprehensive logging for monitoring
✓ Simple testing via management command
✓ Foundation for future notification features
