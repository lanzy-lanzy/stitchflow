# SMS Implementation - Deployment Instructions

## Quick Start (Follow These Steps)

### Step 1: Get Your API Key (2 minutes)

1. Visit: https://semaphore.co
2. Sign up for free account (if not already)
3. Go to Dashboard
4. Copy your API key

**Save this key!** You'll need it in Step 2.

### Step 2: Set Environment Variable (1 minute)

Choose your method based on your OS:

#### Windows Command Prompt
```cmd
set SEMAPHORE_API_KEY=paste-your-api-key-here
python manage.py runserver
```

#### Windows PowerShell
```powershell
$env:SEMAPHORE_API_KEY="paste-your-api-key-here"
python manage.py runserver
```

#### macOS / Linux
```bash
export SEMAPHORE_API_KEY="paste-your-api-key-here"
python manage.py runserver
```

#### Or add to .env file (development)
Create or edit `.env` file in project root:
```
SEMAPHORE_API_KEY=paste-your-api-key-here
```

Then install python-dotenv and load it in settings.py.

### Step 3: Test SMS Works (1 minute)

Run this command:
```bash
python manage.py test_sms 09998887777
```

**Expected Output:**
```
Sending test SMS to 09998887777...
✓ SMS sent successfully!
Response: [{'message_id': '12345678', 'status': 'Sent', ...}]
```

**If you see ✓ SMS sent successfully! → SMS is working!**

### Step 4: Test Real Task Approval (2 minutes)

1. Log in to Admin Dashboard
2. Go to "Manage Tasks"
3. Find a task with status "COMPLETED"
4. Click the approve button (✓)
5. You should see: **"Task approved successfully. Commission created. Customer notified via SMS."**

**If you see this message → SMS integration is working!**

### Step 5: Done!

SMS now automatically sends when admin approves a task.

---

## What Happens When Task is Approved

```
ADMIN CLICKS APPROVE
        ↓
Task status changes to APPROVED
        ↓
Commission created
        ↓
SMS AUTOMATICALLY SENT to customer:
"Hi {customer_name}, your garment for Order #{order_id} 
 is ready for pickup at El Senior Dumingag. Thank you!"
        ↓
Admin sees: "Customer notified via SMS ✓"
        ↓
Customer receives SMS on their phone
```

---

## Troubleshooting

### Problem: "API key not configured"

**Solution:**
```bash
# Make sure environment variable is set
# Windows:
set SEMAPHORE_API_KEY=your-key
# Linux/macOS:
export SEMAPHORE_API_KEY="your-key"

# Then restart Django
python manage.py runserver
```

### Problem: "SMS not received by customer"

**Check:**
1. Customer has phone number in database
2. Phone number format is correct (09998887777)
3. Check application logs for errors
4. Try test command: `python manage.py test_sms 09998887777`

### Problem: "SMS API returned status 401"

**Solution:**
1. Verify API key is correct
2. Copy it again from Semaphore dashboard
3. Update environment variable
4. Restart application

### Problem: "Phone number not provided"

**Solution:**
1. Go to Manage Customers
2. Edit the customer record
3. Make sure phone number is filled in
4. Save the customer
5. Try approving task again

### Problem: "Connection timeout"

**Solution:**
1. Check your internet connection
2. Wait a moment and try again
3. Verify Semaphore API is up (https://semaphore.co)
4. Check application logs for details

---

## Configuration Checklist

Before deploying to production, verify:

- [ ] Semaphore account created at https://semaphore.co
- [ ] API key copied from dashboard
- [ ] API key set in environment variable
- [ ] Test SMS command runs successfully
- [ ] Task approval SMS tested in Manage Tasks
- [ ] Customer phone numbers are in database
- [ ] Message displayed to admin shows "Customer notified via SMS"
- [ ] Application logs show SMS success
- [ ] All error cases tested

---

## Files Modified

### Code Changes
- `etailoring/sms_service.py` - New SMS service
- `etailoring/views.py` - Added SMS in task approval
- `stitchflow/settings.py` - Added Semaphore configuration
- `templates/manage_tasks.html` - Updated success message
- `etailoring/management/commands/test_sms.py` - New test command
- `requirements.txt` - Added requests library

### Documentation
- 13+ comprehensive guides for setup, testing, and troubleshooting

---

## What SMS Customers Receive

**Message:**
```
Hi Maria Santos, your garment for Order #15 is ready for pickup at El Senior Dumingag. Thank you!
```

**Details:**
- Sender: elsenior
- Time: Instant (when admin approves task)
- Length: 107 characters (1 SMS credit)
- Format: Professional and courteous

---

## How to Customize Message

If you want to change the SMS message text:

**File:** `etailoring/sms_service.py` (Line 92)

Current message:
```python
message = f"Hi {customer_name}, your garment for Order #{order_id} is ready for pickup at El Senior Dumingag. Thank you!"
```

Edit to customize. Examples:

**Shorter version:**
```python
message = f"Hi {customer_name}, Order #{order_id} ready for pickup at El Senior!"
```

**With hours:**
```python
message = f"Hi {customer_name}, Order #{order_id} ready! Pickup Mon-Fri 8am-6pm at El Senior Dumingag. Thank you!"
```

Then restart Django.

---

## Monitoring & Logs

### Check if SMS Was Sent

1. Go to Admin Dashboard
2. Check the task approval success message
3. Message should say: "Customer notified via SMS"

### View Detailed Logs

Check Django logs for SMS confirmations:

```
INFO: SMS sent successfully to 09998887777. Message ID: 12345678, Status: Sent
INFO: SMS notification sent to customer Maria Santos for Order #15
```

### Debug Errors

If SMS fails, logs will show:

```
ERROR: SMS API returned status 401: Invalid API key
WARNING: Failed to send SMS to Maria Santos: ...
ERROR: Phone number not provided
```

---

## FAQ

**Q: Do I need to change any other code?**
A: No. Just set the API key, and SMS works automatically.

**Q: Will SMS failure break the task approval?**
A: No. SMS is non-blocking. Task approves even if SMS fails.

**Q: What if customer doesn't have a phone number?**
A: SMS silently fails and is logged. Task approval still succeeds.

**Q: Can I test without approving a task?**
A: Yes: `python manage.py test_sms 09998887777`

**Q: What phone number formats work?**
A: Philippine (09998887777) or International (+639998887777)

**Q: How much does SMS cost?**
A: 1 SMS credit per 160 characters. Our message uses 1 credit.

**Q: Can I change the message?**
A: Yes, edit `etailoring/sms_service.py` line 92.

**Q: Can I change the sender name?**
A: Yes, currently set to "elsenior" in settings.py.

**Q: Is SMS secure?**
A: API key stored in environment variable (secure). Phone numbers used only for SMS.

**Q: Can I send SMS to multiple customers?**
A: Current implementation sends per-task. Bulk SMS possible with Semaphore API.

---

## Production Deployment

### Pre-Deployment
- [ ] Test SMS working locally
- [ ] Verify task approval SMS works
- [ ] Check logs for success messages
- [ ] Review message template
- [ ] Test with different phone numbers
- [ ] Get API key for production Semaphore account

### Deployment
1. Set SEMAPHORE_API_KEY in production environment
2. Deploy code changes
3. Restart Django application
4. Test SMS in production
5. Monitor logs

### Post-Deployment
- [ ] Monitor SMS delivery
- [ ] Check logs regularly
- [ ] Verify customers receive SMS
- [ ] Track any errors
- [ ] Be ready to adjust message if needed

---

## Support Resources

| Resource | URL |
|----------|-----|
| Semaphore API Docs | https://semaphore.co/docs |
| Semaphore Dashboard | https://semaphore.co/dashboard |
| Semaphore Status | https://status.semaphore.co |
| API Endpoint | https://api.semaphore.co/api/v4/messages |

---

## Documentation Files

For more detailed information, see:

1. **FINAL_VERIFICATION.md** - Complete verification checklist
2. **SEMAPHORE_API_REFERENCE.md** - Official API specification
3. **SEMAPHORE_INTEGRATION_GUIDE.md** - Technical implementation details
4. **SMS_MESSAGE_EXAMPLES.md** - Message examples and scenarios
5. **SMS_QUICKSTART.md** - 5-minute quick start
6. **SMS_TESTING_GUIDE.md** - Comprehensive testing procedures
7. **IMPLEMENTATION_COMPLETE.md** - Implementation overview

---

## Summary

✓ **Setup Time:** ~5 minutes (just set API key and test)
✓ **Configuration:** 1 environment variable
✓ **Testing:** Built-in management command
✓ **Reliability:** Full error handling
✓ **Security:** API key in environment variable
✓ **Production:** Ready to deploy

---

## Next Steps

1. **Get API Key** from https://semaphore.co
2. **Set environment variable:** `export SEMAPHORE_API_KEY="your-key"`
3. **Test SMS:** `python manage.py test_sms 09998887777`
4. **Test task approval** in Manage Tasks
5. **Deploy to production** when ready

---

**That's it! SMS is now ready to use.** 🎉✓

For questions, refer to the documentation files above or check the Semaphore API documentation.
