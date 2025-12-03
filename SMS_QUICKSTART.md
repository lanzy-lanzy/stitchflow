# SMS Implementation - Quick Start Guide

## 5-Minute Setup

### Step 1: Get API Key (2 minutes)
1. Visit https://semaphore.co
2. Sign up for free account
3. Go to Dashboard → Get API Key
4. Copy your API key

### Step 2: Set Environment Variable (1 minute)

**Windows (Command Prompt):**
```cmd
set SEMAPHORE_API_KEY=your-api-key-here
python manage.py runserver
```

**Windows (PowerShell):**
```powershell
$env:SEMAPHORE_API_KEY="your-api-key-here"
python manage.py runserver
```

**macOS/Linux:**
```bash
export SEMAPHORE_API_KEY="your-api-key-here"
python manage.py runserver
```

**Or create a `.env` file in project root:**
```
SEMAPHORE_API_KEY=your-api-key-here
```

Then install python-dotenv and load it in settings.py.

### Step 3: Test SMS (1 minute)
```bash
python manage.py test_sms 09998887777
```

Expected output:
```
✓ SMS sent successfully!
Response: {...}
```

### Step 4: Start Using It (1 minute)

The SMS is **automatically sent** when:
1. Admin approves a completed task in Manage Tasks
2. Customer gets SMS notification: 
   ```
   Hi [Name], your garment for Order #[ID] is ready for pickup at El Senior Dumingag. Thank you!
   ```

## That's It!

Your SMS integration is ready to use. No code changes needed.

## What Happens Behind the Scenes

```
Admin clicks "Approve Task" 
    ↓
Task marked as COMPLETED → APPROVED
    ↓
Commission created for tailor
    ↓
SMS sent to customer automatically
    ↓
Success notification shown to admin
```

## Troubleshooting

### Test fails with "API key not configured"
- Check environment variable is set correctly
- Restart the application
- Verify in Django shell: `from django.conf import settings; print(settings.SEMAPHORE_API_KEY)`

### Test fails with "API returned 401"
- Check API key is correct
- Generate new key from Semaphore dashboard
- Wait a moment and try again

### SMS not received by customer
- Verify phone number is correct and in database
- Check logs for errors
- Verify Semaphore account has credits (Semaphore gives free credits)

## File Reference

- **SMS Service:** `etailoring/sms_service.py`
- **Configuration:** `stitchflow/settings.py` (SEMAPHORE_API_KEY)
- **Task Approval:** `etailoring/views.py` (approve_task function)
- **UI Update:** `templates/manage_tasks.html`
- **Test Command:** `etailoring/management/commands/test_sms.py`

## Advanced Configuration

### Change Sender Name
Edit `stitchflow/settings.py`:
```python
SEMAPHORE_SENDER_NAME = 'Your Company Name'
```

### Custom Message Template
Edit `etailoring/sms_service.py`, find `notify_customer_ready_for_pickup()`:
```python
message = f"Your custom message here for {customer_name}..."
```

### Production Checklist
- [ ] API key is in environment variable (not hardcoded)
- [ ] Phone numbers are validated before SMS
- [ ] Error logs are monitored
- [ ] SMS history is being logged
- [ ] Test SMS was successful
- [ ] Task approval SMS works end-to-end

## Support

- Semaphore Help: https://semaphore.co/docs
- API Docs: https://semaphore.co/api/v4/messages
- Dashboard: https://semaphore.co/dashboard

## Next Steps

- [ ] Complete setup above
- [ ] Test with `python manage.py test_sms`
- [ ] Approve a test task to verify SMS works
- [ ] Review logs: `SMS_IMPLEMENTATION.md`
- [ ] Add additional notifications (tailor alerts, payment reminders, etc.)
