# SMS Testing and Debugging Guide

## Testing Methods

### Method 1: Management Command (Recommended)

#### Basic Test
```bash
python manage.py test_sms 09998887777
```

#### Test with Custom Data
```bash
python manage.py test_sms 09998887777 \
  --customer-name "Maria Santos" \
  --order-id 42
```

#### Expected Success Output
```
Sending test SMS to 09998887777...
✓ SMS sent successfully!
Response: {...}
```

#### Expected Failure Output
```
Sending test SMS to 09998887777...
✗ Failed to send SMS
Error: Semaphore API key not configured
```

### Method 2: Django Shell

```bash
python manage.py shell
```

Then run:
```python
from etailoring.sms_service import SemaphoreSMS
from etailoring.models import Customer, Task

# Test direct SMS
success, response = SemaphoreSMS.send_message(
    "Test message",
    "09998887777"
)
print(f"Success: {success}")
print(f"Response: {response}")

# Test customer notification
success, message = SemaphoreSMS.notify_customer_ready_for_pickup(
    customer_name="Juan Dela Cruz",
    customer_phone="09998887777",
    order_id=1
)
print(f"Success: {success}")
print(f"Message: {message}")

# Test with real customer
customer = Customer.objects.first()
success, message = SemaphoreSMS.notify_customer_ready_for_pickup(
    customer_name=customer.user.get_full_name(),
    customer_phone=customer.phone_number,
    order_id=1
)
```

### Method 3: Web UI (End-to-End Test)

1. Go to Admin Dashboard → Manage Tasks
2. Find a completed task
3. Click the approve button (✓)
4. Confirm the approval
5. Check for success notification:
   - Should say "Customer notified via SMS"
6. Verify customer received SMS

### Method 4: API Direct Call

Using curl or Postman:

```bash
curl -X POST http://localhost:8000/api/admin/tasks/1/approve/ \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json"
```

Expected success response:
```json
{
    "detail": "Task approved successfully. Commission created. Customer notified via SMS.",
    "task_id": 1,
    "task_status": "APPROVED",
    "commission_id": 123,
    "commission_amount": "180.00"
}
```

## Checking Configuration

### Verify API Key is Set

**In Django Shell:**
```python
from django.conf import settings

api_key = settings.SEMAPHORE_API_KEY
print(f"API Key configured: {bool(api_key)}")
print(f"API Key starts with: {api_key[:10] if api_key else 'NOT SET'}...")
print(f"Sender Name: {settings.SEMAPHORE_SENDER_NAME}")
```

**From Command Line:**

Windows:
```cmd
echo %SEMAPHORE_API_KEY%
```

Linux/macOS:
```bash
echo $SEMAPHORE_API_KEY
```

### Verify Database Records

```python
from etailoring.models import Customer, Task, Order

# Check customer phone numbers
for customer in Customer.objects.all()[:5]:
    print(f"{customer.user.get_full_name()}: {customer.phone_number}")

# Check task order relationship
task = Task.objects.first()
print(f"Task {task.id} → Order {task.order.id} → Customer {task.order.customer}")
```

## Debugging

### Enable Debug Logging

Add to `stitchflow/settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'etailoring.sms_service': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

### Check Application Logs

```bash
# If using Django development server, check console output
python manage.py runserver
# Look for SMS-related log messages
```

### Common Debug Scenarios

#### Scenario 1: SMS doesn't send silently
```python
# Check if exception was caught
import logging
logger = logging.getLogger('etailoring.sms_service')
logger.setLevel(logging.DEBUG)

# Try manually
from etailoring.sms_service import SemaphoreSMS
success, response = SemaphoreSMS.send_message("Test", "09998887777")
print(f"Result: {success} - {response}")
```

#### Scenario 2: API key issues
```python
# Check configuration
from django.conf import settings
print(settings.SEMAPHORE_API_KEY)

# Test with hardcoded key temporarily (development only)
class TestSMS(SemaphoreSMS):
    API_KEY = "your-test-key"
    
TestSMS.send_message("Test", "09998887777")
```

#### Scenario 3: Phone number issues
```python
# Validate phone number format
phone = "09998887777"
print(f"Phone: {phone}")
print(f"Length: {len(phone)}")
print(f"Starts with 09: {phone.startswith('09')}")
print(f"All digits: {phone.isdigit()}")
```

## Performance Testing

### Load Test: Send Multiple SMS

```python
from etailoring.sms_service import SemaphoreSMS
import time

phone_numbers = [
    "09998887777",
    "09123456789",
    "09987654321",
]

start = time.time()
for phone in phone_numbers:
    success, response = SemaphoreSMS.notify_customer_ready_for_pickup(
        "Test Customer",
        phone,
        1
    )
    print(f"{phone}: {'✓' if success else '✗'}")

elapsed = time.time() - start
print(f"Sent {len(phone_numbers)} SMS in {elapsed:.2f}s")
```

## Monitoring

### Check SMS Service Health

Create a simple health check:

```python
# health_check.py
from etailoring.sms_service import SemaphoreSMS
from django.conf import settings

def check_sms_service():
    """Quick SMS service health check"""
    
    # 1. Check configuration
    if not settings.SEMAPHORE_API_KEY:
        return "FAIL", "API key not configured"
    
    if settings.SEMAPHORE_API_KEY == "your-api-key-here":
        return "FAIL", "API key still has placeholder value"
    
    # 2. Try sending test message
    success, response = SemaphoreSMS.send_message(
        "Health check test",
        "09998887777"
    )
    
    if success:
        return "OK", "SMS service operational"
    else:
        return "WARN", f"SMS service issue: {response}"

if __name__ == "__main__":
    status, message = check_sms_service()
    print(f"Status: {status}")
    print(f"Message: {message}")
```

Run it:
```bash
python manage.py shell < health_check.py
```

## Logs Location

Django logs location depends on configuration. By default:
- **Development:** Console output (when running `runserver`)
- **Production:** Check `LOGGING` configuration in `settings.py`

Example log entries:
```
[INFO] 2024-01-15 10:30:45,123 etailoring.sms_service: SMS sent to 09998887777. Status: 200
[INFO] 2024-01-15 10:30:46,456 etailoring.sms_service: Successfully sent ready-for-pickup SMS to 09998887777
[WARNING] 2024-01-15 10:31:00,789 etailoring.sms_service: Failed to send SMS to 09998887777: API returned 401
```

## Error Response Codes

### Common Semaphore API Responses

| Status | Meaning | Solution |
|--------|---------|----------|
| 200 | Success | None needed |
| 400 | Bad request | Check phone number format |
| 401 | Unauthorized | Verify API key |
| 403 | Forbidden | Check API key permissions |
| 429 | Rate limited | Wait before retry |
| 500 | Server error | Try again later |

## Troubleshooting Checklist

- [ ] API key is set (not placeholder)
- [ ] Customer has phone number in database
- [ ] Phone number format is valid (09XXXXXXXXX)
- [ ] Semaphore account has credits
- [ ] No network/firewall blocking requests
- [ ] requests library is installed (`pip list | grep requests`)
- [ ] Test SMS command runs successfully
- [ ] Task approval shows "Customer notified via SMS"
- [ ] Check logs for error messages

## Testing on Different Environments

### Development
```bash
export SEMAPHORE_API_KEY="your-test-key"
python manage.py runserver
# Monitor console for SMS logs
```

### Staging/Production
```bash
# Set in .env file or environment
SEMAPHORE_API_KEY=your-production-key

# Check logs
tail -f /var/log/django.log | grep SMS
```

## Test Data Setup

Create test records:

```python
from django.contrib.auth.models import User
from etailoring.models import Customer, Order, Tailor, Task, Fabric

# Create test customer with phone
user = User.objects.create_user(
    username='testcustomer',
    first_name='Test',
    last_name='Customer',
    email='test@example.com'
)
customer = Customer.objects.create(
    user=user,
    phone_number='09998887777',
    address='Test Address'
)

# Create fabric
fabric = Fabric.objects.create(
    name='Test Fabric',
    unit_type='METERS',
    price_per_unit=100
)

# Create order
order = Order.objects.create(
    customer=customer,
    fabric=fabric,
    garment_type='BLOUSE',
    total_amount=500
)

# Create tailor
tailor_user = User.objects.create_user(username='testtailor')
tailor = Tailor.objects.create(user=tailor_user, phone_number='09111111111')

# Create and mark task as completed
task = Task.objects.create(order=order, tailor=tailor, status='COMPLETED')
print(f"Created test task: {task.id}")
```

Then approve the task via API or admin interface to trigger SMS.
