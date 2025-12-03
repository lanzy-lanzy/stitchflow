# Semaphore SMS API Reference & Implementation Guide

## Official Documentation Reference
- **API Documentation:** https://semaphore.co/docs
- **API Endpoint:** POST https://api.semaphore.co/api/v4/messages
- **Rate Limit:** 120 requests per minute
- **Pricing:** 1 credit per 160 characters

## Implementation Details for StitchFlow

### Setup

Your SMS implementation is configured to use:
- **API Endpoint:** `https://api.semaphore.co/api/v4/messages`
- **Sender Name:** `elsenior` (El Senior Dumingag)
- **API Key:** Set via `SEMAPHORE_API_KEY` environment variable

### API Request Format

```http
POST https://api.semaphore.co/api/v4/messages?apikey=YOUR_KEY&sendername=elsenior&message=Hello&number=09998887777
```

### Required Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `apikey` | Your Semaphore API key (from dashboard) | `fa0f4ff77ba74de0b8e74be14735e951` |
| `number` | Recipient phone number | `09998887777` or `+639998887777` |
| `message` | SMS message content | `Hi Maria, your order is ready!` |

### Optional Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `sendername` | Sender name displayed on phone | `SEMAPHORE` |

**For StitchFlow:** `sendername=elsenior`

### Message Guidelines

✓ **Maximum Length:** 160 characters per SMS
- Messages longer than 160 characters are automatically split
- Example: 320 character message = 2 SMS credits

✓ **What NOT to do:**
- DO NOT start message with "TEST" - Semaphore silently ignores these
- Our implementation warns if a message starts with TEST

✓ **Supported Characters:**
- Standard ASCII characters (A-Z, a-z, 0-9)
- Special characters (! @ # $ % ^ & * etc.)
- Philippine Peso symbol (₱)

✓ **Examples:**
```
Good: "Hi Maria, your garment is ready for pickup!"
Good: "Order #42 - Ready! Please come get it. - elsenior"
Bad:  "TEST Message" ← Will be ignored by Semaphore
Bad:  "Á É Í Ó Ú" ← Non-ASCII might not display correctly
```

## API Response Format

### Success Response (HTTP 200)

```json
[
  {
    "message_id": "12345678",
    "user_id": "9876",
    "user": "admin@example.com",
    "account_id": "5432",
    "account": "El Senior Dumingag",
    "recipient": "09998887777",
    "message": "Hi Maria, your garment is ready!",
    "sender_name": "elsenior",
    "network": "globe",
    "status": "Sent",
    "type": "single",
    "source": "api",
    "created_at": "2024-01-15 10:30:45"
  }
]
```

### Response Fields

| Field | Meaning | Possible Values |
|-------|---------|-----------------|
| `message_id` | Unique SMS identifier | Number |
| `status` | Current SMS status | Pending, Sent, Failed, Refunded |
| `recipient` | Phone number sent to | 09998887777 |
| `sender_name` | Name shown on phone | elsenior |
| `network` | Telco network | globe, smart, sun, dito |
| `created_at` | When SMS was sent | Timestamp |

### Status Meanings

- **Pending:** SMS in transit to network
- **Sent:** Successfully delivered to network
- **Failed:** Rejected by network, will be refunded
- **Refunded:** Credit refunded to account

## Error Handling

### Common Error Codes

| HTTP Status | Meaning | Solution |
|-------------|---------|----------|
| 200 | Success | No action needed |
| 400 | Bad request | Check parameters (apikey, number, message) |
| 401 | Unauthorized | Verify API key is correct |
| 403 | Forbidden | Check API key permissions |
| 429 | Rate limited | Exceeded 120 requests/minute limit |
| 500 | Server error | Try again later |

### Error Response Example

```json
{
  "error": "Invalid API key"
}
```

### Our Implementation Handles

```python
# In sms_service.py - send_message()

✓ API key validation
✓ Phone number validation
✓ Message content validation
✓ TEST prefix warning (Semaphore quirk)
✓ HTTP status code checking
✓ JSON parsing errors
✓ Network timeouts (10 second limit)
✓ Connection errors
✓ Detailed error logging
```

## Current Implementation

### File: `etailoring/sms_service.py`

```python
class SemaphoreSMS:
    """Send SMS via Semaphore API"""
    
    API_KEY = os.getenv('SEMAPHORE_API_KEY', '')
    SENDER_NAME = 'elsenior'
    API_URL = 'https://api.semaphore.co/api/v4/messages'
    
    @classmethod
    def send_message(cls, message, number):
        """Send SMS to a phone number"""
        # Validates inputs
        # Builds request with proper parameters
        # Handles all errors gracefully
        # Logs everything for debugging
        
    @classmethod
    def notify_customer_ready_for_pickup(cls, customer_name, customer_phone, order_id):
        """Notify customer their garment is ready"""
        # Builds pickup message
        # Sends via send_message()
        # Returns success/failure
```

## Integration with Task Approval

When admin approves a task in **Manage Tasks**:

```
1. Admin clicks approve button
   ↓
2. Django calls approve_task() in views.py
   ↓
3. Task marked as COMPLETED → APPROVED
   ↓
4. Commission created for tailor
   ↓
5. SMS Service invoked:
   - Retrieves customer name from database
   - Retrieves customer phone from database
   - Calls SemaphoreSMS.notify_customer_ready_for_pickup()
   - Message: "Hi {name}, your garment for Order #{id} is ready for 
              pickup at El Senior Dumingag. Thank you!"
   - SMS sent via Semaphore API
   ↓
6. Result logged
   ↓
7. Admin sees: "Customer notified via SMS ✓"
   ↓
8. Task approval completes successfully
   (even if SMS fails - non-blocking)
```

## Configuration Details

### File: `stitchflow/settings.py`

```python
# Semaphore SMS Configuration
SEMAPHORE_API_KEY = os.getenv('SEMAPHORE_API_KEY', 'your-api-key-here')
SEMAPHORE_SENDER_NAME = 'elsenior'
```

### Environment Setup

**Windows Command Prompt:**
```cmd
set SEMAPHORE_API_KEY=your-api-key
python manage.py runserver
```

**Windows PowerShell:**
```powershell
$env:SEMAPHORE_API_KEY="your-api-key"
python manage.py runserver
```

**macOS/Linux:**
```bash
export SEMAPHORE_API_KEY="your-api-key"
python manage.py runserver
```

**Or in `.env` file:**
```
SEMAPHORE_API_KEY=your-api-key
```

Then load with python-dotenv.

## Testing

### Quick Test via Management Command

```bash
python manage.py test_sms 09998887777
python manage.py test_sms 09998887777 --customer-name "Maria" --order-id 42
```

### Test via Django Shell

```python
from etailoring.sms_service import SemaphoreSMS

# Send test SMS
success, response = SemaphoreSMS.send_message(
    "Test message from elsenior",
    "09998887777"
)
print(f"Success: {success}")
print(f"Response: {response}")

# Send customer notification
success, msg = SemaphoreSMS.notify_customer_ready_for_pickup(
    "Maria Santos",
    "09998887777",
    15
)
print(f"Success: {success}")
print(f"Message: {msg}")
```

### Test via Web UI

1. Go to Admin Dashboard → Manage Tasks
2. Find a task with status "COMPLETED"
3. Click the approve button (✓)
4. Success message should show: "Customer notified via SMS"
5. Check logs to verify SMS was sent

## API Rate Limiting

**Rate Limit:** 120 requests per minute

If you hit the limit:
- Implement request queuing
- Space out requests
- Use bulk messaging (multiple recipients in one request)

For bulk messages:
```
number=09998887777,09123456789,09987654321
```

## Monitoring & Logging

All SMS operations are logged with:

### INFO Level
```
SMS API response: Status 200 for number 09998887777
SMS sent successfully to 09998887777. Message ID: 12345678, Status: Sent
Successfully sent ready-for-pickup SMS to 09998887777
```

### WARNING Level
```
Message to 09998887777 starts with TEST - may be silently ignored by Semaphore
Unexpected response format from Semaphore: {...}
```

### ERROR Level
```
Semaphore API key not configured
Phone number not provided
Message content is required
SMS API returned status 401: {"error": "Invalid API key"}
SMS API request timeout (exceeded 10 seconds)
SMS API connection error - unable to reach Semaphore
```

## Account Management

### Check Your Account

Visit: https://semaphore.co/dashboard

**Available Actions:**
- View SMS balance/credits
- Manage Sender Names
- View message history
- Add users to account
- Manage billing

### Add Sender Name "elsenior"

1. Log in to Semaphore Dashboard
2. Go to Account → Sender Names
3. Click "Add New Sender Name"
4. Enter: `elsenior`
5. Wait for approval (usually instant)
6. Use in SMS: `sendername=elsenior`

## Troubleshooting

### "API key not configured"
```
Cause: SEMAPHORE_API_KEY environment variable not set
Fix: export SEMAPHORE_API_KEY="your-key"
     Then restart Django application
```

### "SMS API returned status 401"
```
Cause: API key is invalid or expired
Fix: Verify API key from Semaphore dashboard
     Generate new key if needed
     Update environment variable
```

### "SMS API returned status 429"
```
Cause: Exceeded 120 requests per minute
Fix: Space out requests
     Or use bulk messaging (comma-separated numbers)
     Wait 1 minute before retrying
```

### "Message silently not sent"
```
Cause: Message starts with "TEST"
Fix: Never start SMS with "TEST"
    Semaphore silently ignores these for spam protection
    Our code logs a warning if this happens
```

### "Request timeout"
```
Cause: Semaphore API not responding
Fix: Check internet connection
    Verify Semaphore status (https://status.semaphore.co)
    Try again after a few seconds
    Check application logs for details
```

## Best Practices

✓ **Validation**
- Always validate phone numbers before sending
- Check message length before sending
- Sanitize user input

✓ **Error Handling**
- Catch and log all errors
- Don't let SMS failures break other operations
- Inform user if SMS fails, but allow task to complete

✓ **Rate Limiting**
- Monitor your request rate
- Implement queuing for bulk SMS
- Don't exceed 120 requests/minute

✓ **Message Design**
- Keep messages clear and concise
- Include important info (Order ID, location)
- Be professional and courteous
- Avoid marketing spam

✓ **Testing**
- Test with different phone numbers
- Test different message lengths
- Monitor message statuses
- Check delivery receipts

## Sample Messages

### Customer Ready Notification (Current)
```
Hi Maria Santos, your garment for Order #42 is ready for pickup 
at El Senior Dumingag. Thank you!
```
Length: 106 characters (1 SMS credit)

### Commission Notification (Future)
```
Hi Jose Cruz, commission of ₱500.00 for Order #42 has been approved. 
Please contact admin for payment.
```
Length: 114 characters (1 SMS credit)

### Multi-SMS Example
```
Msg 1: "Hi Maria, your order #42 is complete! Your blouse is ready for 
        pickup. Please visit El Senior Dumingag at your earliest..."
Msg 2: "...convenience. We are open Mon-Fri 8am-5pm. Thank you for your 
        business!"
```
Length: ~320 characters total (2 SMS credits)

## API Limits Summary

| Limit | Value |
|-------|-------|
| Characters per SMS | 160 |
| Max recipients per request | 1,000 |
| Requests per minute | 120 |
| Timeout | 10 seconds |
| Credit per SMS | 1 |

## Related Files

- **Service:** `etailoring/sms_service.py`
- **Configuration:** `stitchflow/settings.py`
- **Integration:** `etailoring/views.py` (approve_task function)
- **UI:** `templates/manage_tasks.html`
- **Test Command:** `etailoring/management/commands/test_sms.py`
- **Documentation:** This file

## Summary

✓ **API Endpoint:** https://api.semaphore.co/api/v4/messages
✓ **Sender Name:** elsenior
✓ **Rate Limit:** 120 requests/minute
✓ **Message Length:** 160 characters max
✓ **Authentication:** API key via query parameter
✓ **Response:** JSON with message_id, status, recipient
✓ **Error Handling:** HTTP status codes + JSON error responses
✓ **Implementation:** Fully integrated in task approval workflow
✓ **Logging:** Comprehensive logging for debugging
✓ **Testing:** Built-in management command

**Reference:** https://semaphore.co/docs
